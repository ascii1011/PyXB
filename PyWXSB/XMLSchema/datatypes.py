"""Classes supporting XMLSchema Part 2: Datatypes"""

import structures as xsc

_PrimitiveDatatypes = []
_DerivedDatatypes = []
_ListDatatypes = []

class anySimpleType (xsc.PythonSimpleTypeSupport):
    def stringToPython (self, value):
        return value

    def pythonToString (self, value):
        return value
# anySimpleType is not treated as a primitive, because its variety must be absent (not atomic).
    
class string (anySimpleType):
    def stringToPython (self, value):
        return value

    def pythonToString (self, value):
        return value
_PrimitiveDatatypes.append(string)

class boolean (anySimpleType):
    def stringToPython (self, value):
        if 'true' == value:
            return True
        if 'false' == value:
            return False
        raise ValueError('%s: Invalid string "%s"' % (self._simpleTypeDefinition.name(),))
    def pythonToString (self, value):
        if value:
            return 'true'
        return 'false'
_PrimitiveDatatypes.append(boolean)

class decimal (anySimpleType):
    pass
_PrimitiveDatatypes.append(decimal)

class float (anySimpleType):
    pass
_PrimitiveDatatypes.append(float)

class double (anySimpleType):
    pass
_PrimitiveDatatypes.append(double)

class duration (anySimpleType):
    pass
_PrimitiveDatatypes.append(duration)

class dateTime (anySimpleType):
    pass
_PrimitiveDatatypes.append(dateTime)

class time (anySimpleType):
    pass
_PrimitiveDatatypes.append(time)

class date (anySimpleType):
    pass
_PrimitiveDatatypes.append(date)

class gYearMonth (anySimpleType):
    pass
_PrimitiveDatatypes.append(gYearMonth)

class gYear (anySimpleType):
    pass
_PrimitiveDatatypes.append(gYear)

class gMonthDay (anySimpleType):
    pass
_PrimitiveDatatypes.append(gMonthDay)

class gDay (anySimpleType):
    pass
_PrimitiveDatatypes.append(gDay)

class gMonth (anySimpleType):
    pass
_PrimitiveDatatypes.append(gMonth)

class hexBinary (anySimpleType):
    pass
_PrimitiveDatatypes.append(hexBinary)

class base64Binary (anySimpleType):
    pass
_PrimitiveDatatypes.append(base64Binary)

class anyURI (anySimpleType):
    pass
_PrimitiveDatatypes.append(anyURI)

class QName (anySimpleType):
    pass
_PrimitiveDatatypes.append(QName)

class NOTATION (anySimpleType):
    pass
_PrimitiveDatatypes.append(NOTATION)

class normalizedString (string):
    pass
_DerivedDatatypes.append(normalizedString)

class token (normalizedString):
    pass
_DerivedDatatypes.append(token)

class language (token):
    pass
_DerivedDatatypes.append(language)

class NMTOKEN (token):
    pass
_DerivedDatatypes.append(NMTOKEN)
_ListDatatypes.append( ( 'NMTOKENS', 'NMTOKEN' ) )

class Name (token):
    pass
_DerivedDatatypes.append(Name)

class NCName (Name):
    pass
_DerivedDatatypes.append(NCName)

class ID (NCName):
    pass
_DerivedDatatypes.append(ID)

class IDREF (NCName):
    pass
_DerivedDatatypes.append(IDREF)
_ListDatatypes.append( ( 'IDREFS', 'IDREF' ) )

class ENTITY (NCName):
    pass
_DerivedDatatypes.append(ENTITY)
_ListDatatypes.append( ( 'ENTITIES', 'ENTITY' ) )

class integer (decimal):
    pass
_DerivedDatatypes.append(integer)

class nonPositiveInteger (integer):
    pass
_DerivedDatatypes.append(nonPositiveInteger)

class negativeInteger (nonPositiveInteger):
    pass
_DerivedDatatypes.append(negativeInteger)

class long (integer):
    pass
_DerivedDatatypes.append(long)

class int (long):
    pass
_DerivedDatatypes.append(int)

class short (int):
    pass
_DerivedDatatypes.append(short)

class byte (short):
    pass
_DerivedDatatypes.append(byte)

class nonNegativeInteger (integer):
    pass
_DerivedDatatypes.append(nonNegativeInteger)

class unsignedLong (nonNegativeInteger):
    pass
_DerivedDatatypes.append(unsignedLong)

class unsignedInt (unsignedLong):
    pass
_DerivedDatatypes.append(unsignedInt)

class unsignedShort (unsignedInt):
    pass
_DerivedDatatypes.append(unsignedShort)

class unsignedByte (unsignedShort):
    pass
_DerivedDatatypes.append(unsignedByte)

class positiveInteger (nonNegativeInteger):
    pass
_DerivedDatatypes.append(positiveInteger)

def DefineSimpleTypes (schema):
    # Add the simple ur type
    schema._addTypeDefinition(xsc.SimpleTypeDefinition.SimpleUrTypeDefinition(schema.getTargetNamespace()))
    # Add definitions for all primitive and derived simple types
    pts_std_map = {}
    for dtc in _PrimitiveDatatypes:
        name = dtc.__name__.rstrip('_')
        pts_std_map.setdefault(dtc, schema._addTypeDefinition(xsc.SimpleTypeDefinition.CreatePrimitiveInstance(name, schema.getTargetNamespace(), dtc())))
    for dtc in _DerivedDatatypes:
        name = dtc.__name__.rstrip('_')
        parent_std = pts_std_map[dtc.SuperType()]
        pts_std_map.setdefault(dtc, schema._addTypeDefinition(xsc.SimpleTypeDefinition.CreateDerivedInstance(name, schema.getTargetNamespace(), parent_std, dtc())))
    for (list_name, element_name) in _ListDatatypes:
        element_std = schema._lookupTypeDefinition(element_name)
        schema._addTypeDefinition(xsc.SimpleTypeDefinition.CreateListInstance(list_name, schema.getTargetNamespace(), element_std))
