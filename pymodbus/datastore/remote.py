"""Remote datastore."""
import logging

from pymodbus.exceptions import NotImplementedException
from pymodbus.interfaces import IModbusSlaveContext

#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
_logger = logging.getLogger(__name__)


#---------------------------------------------------------------------------#
# Context
#---------------------------------------------------------------------------#
class RemoteSlaveContext(IModbusSlaveContext):
    ''' TODO
    This creates a modbus data model that connects to
    a remote device (depending on the client used)
    '''

    def __init__(self, client, unit=None):
        ''' Initializes the datastores

        :param client: The client to retrieve values with
        :param unit: Unit ID of the remote slave
        '''
        self._client = client
        self.unit = unit
        self.__build_mapping()

    def reset(self):
        ''' Resets all the datastores to their default values '''
        raise NotImplementedException()

    def validate(self, fc_as_hex, address, count=1): # pylint: disable=arguments-renamed
        ''' Validates the request to make sure it is in range

        :param fc_as_hex: The function we are working with
        :param address: The starting address
        :param count: The number of values to test
        :returns: True if the request in within range, False otherwise
        '''
        txt = f"validate[{fc_as_hex}] {address}:{count}"
        _logger.debug(txt)
        result = self.__get_callbacks[self.decode(fc_as_hex)](address, count)
        return not result.isError()

    def getValues(self, fc_as_hex, address, count=1): # pylint: disable=arguments-renamed
        ''' Get `count` values from datastore

        :param fc_as_hex: The function we are working with
        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        '''
        #NOSONAR TODO deal with deferreds pylint: disable=fixme
        txt = f"get values[{fc_as_hex}] {address}:{count}"
        _logger.debug(txt)
        result = self.__get_callbacks[self.decode(fc_as_hex)](address, count)
        return self.__extract_result(self.decode(fc_as_hex), result)

    def setValues(self, fc_as_hex, address, values): # pylint: disable=arguments-renamed
        ''' Sets the datastore with the supplied values

        :param fc_as_hex: The function we are working with
        :param address: The starting address
        :param values: The new values to be set
        '''
        #NOSONAR TODO deal with deferreds pylint: disable=fixme
        txt = f"set values[{fc_as_hex}] {address}:{len(values)}"
        _logger.debug(txt)
        self.__set_callbacks[self.decode(fc_as_hex)](address, values)

    def __str__(self):
        ''' Returns a string representation of the context

        :returns: A string representation of the context
        '''
        return f"Remote Slave Context({self._client})"

    def __build_mapping(self):
        '''
        A quick helper method to build the function
        code mapper.
        '''
        kwargs = {}
        if self.unit:
            kwargs["unit"] = self.unit
        self.__get_callbacks = {
            'd': lambda a, c: self._client.read_discrete_inputs(a, c, **kwargs), # pylint: disable=unnecessary-lambda
            'c': lambda a, c: self._client.read_coils(a, c, **kwargs), # pylint: disable=unnecessary-lambda
            'h': lambda a, c: self._client.read_holding_registers(a, c, **kwargs), # pylint: disable=unnecessary-lambda
            'i': lambda a, c: self._client.read_input_registers(a, c, **kwargs), # pylint: disable=unnecessary-lambda
        }
        self.__set_callbacks = {
            'd': lambda a, v: self._client.write_coils(a, v, **kwargs), # pylint: disable=unnecessary-lambda
            'c': lambda a, v: self._client.write_coils(a, v, **kwargs), # pylint: disable=unnecessary-lambda
            'h': lambda a, v: self._client.write_registers(a, v, **kwargs), # pylint: disable=unnecessary-lambda
            'i': lambda a, v: self._client.write_registers(a, v, **kwargs), # pylint: disable=unnecessary-lambda
        }

    def __extract_result(self, fc_as_hex, result): # pylint: disable=no-self-use
        ''' A helper method to extract the values out of
        a response.  TODO make this consistent (values?)
        '''
        if not result.isError():
            if fc_as_hex in ['d', 'c']:
                return result.bits
            if fc_as_hex in ['h', 'i']:
                return result.registers
        else:
            return result
        return None
