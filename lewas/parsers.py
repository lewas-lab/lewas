import re

__all__ = [ 'split_parser', 'ParseError' ]

class ParseError(RuntimeError):
    pass

def split_parser(**kwargs):
    return lambda astring: _split_parser(astring, **kwargs)

def _split_parser(astring, **kwargs):
    """regexp: a regular expression that will be applied to the full line, 
               string to parse should be in the first match group
       astring: the string to parse
       delim:   character to split string on
    """
    delim = " "
    if 'delim' in kwargs:
        delim = kwargs['delim']

    if 'regexp' in kwargs:
        try:
            values = regexp.search(astring).group(1).split(delim)
        except AttributeError as e:
            raise ParseError("/{0}/ does not match '{1}'".format(regexp.pattern,astring))
    else:
        values = astring.split(delim)

    if 'types' in kwargs:
        types = kwargs['types']
    else:
        types = [float]*len(values)
        
    if 'helper' in kwargs:
        return [ kwargs['helper'](value) for value in values ]
    else:
        return [ typef(value) for (typef,value) in zip(types,values) ]
            

if __name__ == '__main__':
    import sys
    
    ### Below this is specific to the weather station

    def weather_helper(astring):
        """A helper should take a string representing a single measurement and
        return something.  That list returned by the parser will be
        comprised of elements returned by the helper

        """

        (key, value) = astring.split("=")
        (value,units) = re.search(r'([0-9]+(?:\.[0-9]+)?)([a-zA-Z]+)',value).groups()
        return (value, key, units)

    string1 = "0R5,Th=25.9C,Vh=12.0N,Vs=15.2V\r\n"

    dataregex = re.compile(r'0R[0-5],(.*)')
    values = split_parser(dataregex, string1, ",", helper=weather_helper)
    
    for v in values:
        print(v)

    ### Let's say we have a sensor that just has a simple output
    ### format of comma separated numbers. 

    print("\nAnother sensor")

    string2 = "sensor2: 23.1,34.3,56,34"

    ### We do need to provide the parser an array of units to use and
    ### metrics, presumably we get this from the sensor's
    ### documentation (in this sense, the weather station data format
    ### is rather nice, it allows us to programatically extract unit
    ### information without having to refer to the manual)
    units2 = [ "m/s","mg/L","V","C" ]
    metrics2 = [ "wind speed", "dissolved oxygen", "battery voltage", "temperature" ]
    sensor_regex = re.compile(r'sensor2:\s+(.*)$')
    values = split_parser(sensor_regex, string2, ",", units=units2, metrics=metrics2)

    for m in values:
        print(m)

    ### Example of exception handling

    string3 = "sensor4: hot,cold,warm"
    try:
        values = split_parser(sensor_regex, string3)
    except ParseError as e:
        sys.stderr.write("ParseError: {0}\ncontinuing...\n".format(e))
                
    ### Discussion: requiring that we pass metrics and units arrays to
    ### the parser was not a good design: parsing really doesn't
    ### require that information, it's just the construction of the
    ### Measurement object that does. I changed the definition of
    ### parser to just return a list of coerced values

