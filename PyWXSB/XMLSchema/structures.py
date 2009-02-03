"""Classes corresponding to W3C XML Schema components.

Class names and behavior should conform to the schema components
described in http://www.w3.org/TR/xmlschema-1/.

Each class has a CreateFromDOM class method that creates an instance
and initializes it from a DOM node.

Classes that need to support built-ins also support a
CreateBaseInstance class method that creates a new instance manually.

"""

from PyWXSB import *
from xml.dom import Node
import types

class PythonSimpleTypeSupport(object):
    """Class to support converting between WXS simple types and Python
    native types.

    There must be a one-to-one correspondence between instances of (a
    subclass of) this class and any built-in simple types except
    lists (and unions).

    Schema-defined STDs do not currently provide a mechanism to
    associate a PST.  Instead:

    * Absent types (e.g., restrictions of the ur type) and Atomic
      types use the PST of their base type definition (recursively,
      until a PST is found).
    * Lists use the PST of their item type definition.
    * Unions use the PSTs of their member type definitions.

    Currently, the only built-in non-atomic STDs are list variety, and
    they should use the PST of the underlying itemTypeDefinition just
    as schema-defined STDs do.
    """
    
    # A reference to the XMLSchema.structures.SimpleTypeDefinition
    # instance for which this instance provides support.  The
    # reference is bidirectional through the other side's
    # __pythonSupport variable.  It may be assigned only once, and is
    # done when this instance is bound to an STD.
    __simpleTypeDefinition = None

    @classmethod
    def SuperType (cls):
        """Identify the immediately higher class in the PythonSimpleTypeSupport hierarchy.

        The topmost class in the hierarchy considers itself to be its
        SuperType."""
        if PythonSimpleTypeSupport == cls:
            return cls
        for sc in cls.__bases__:
            if issubclass(sc, PythonSimpleTypeSupport):
                return sc
        raise LogicError('%s: Unable to identify superType' % (cls.__name__,))

    def isUrType (self):
        """Return true if this PSTS instance is at the top level."""
        return PythonSimpleTypeSupport == self.__class__

    def isPrimitiveType (self):
        """Return true iff this PSTS instance is a direct descendent of the urType."""
        return PythonSimpleTypeSupport in self.__class__.__bases__

    def _setSimpleTypeDefinition (self, std):
        """Set the simple type definition corresponding to this PSTS.

        This method should only be invoked by SimpleTypeDefinition."""
        if self.__simpleTypeDefinition:
            raise LogicError('Multiple assignments of SimpleTypeDefinition to PythonSTSupport')
        self.__simpleTypeDefinition = std
        return self

    def simpleTypeDefinition (self):
        """Return a reference to the SimpleTypeDefinition component bound to this type."""
        return self.__simpleTypeDefinition

    def stringToPython (self, value):
        """Convert a value in string form to a native Python data value.

        This method should be overridden in primitive PSTSs.  It is
        invoked as a pass-thru by SimpleTypeDefinition.stringToPython.

        @throw PyWXSB.BadTypeValueError if the value is not
        appropriate for the simple type.
        """
        raise IncompleteImplementationError('%s: Support does not define stringToPython' % (self.__simpleTypeDefinition.name(),))
        
    def pythonToString (self, value):
        """Convert a value in native Python to a string appropriate for the simple type.

        This method should be overridden in primitive PSTSs.  It is
        invoked as a pass-thru by SimpleTypeDefinition.pythonToString
        """
        raise IncompleteImplementationError('%s: Support does not define pythonToString' % (self.__simpleTypeDefinition.name(),))

    @classmethod
    def StringToList (cls, values, item_type_definition):
        """Extract a list of values of the given type from a string.

        This is used for an STD with variety 'list'.
        @todo Implement StringToList
        """
        raise IncompleteImplementationError('PythonSimpleTypeSupport.stringToList')

    @classmethod
    def ListToString (cls, values, item_type_definition):
        """Encode a sequence of values of the given type as a string

        This is used for an STD with variety 'list'.
        @todo Implement ListToString"""
        raise IncompleteImplementationError('PythonSimpleTypeSupport.StringToList')

    @classmethod
    def StringToUnion (cls, values, member_type_definitions):
        """Extract a value of one of the given types from a string.

        This is used for an STD with variety 'union'.
        @todo Implement StringToUnion"""
        raise IncompleteImplementationError('PythonSimpleTypeSupport.stringToUnion')

    @classmethod
    def UnionToString (cls, values, member_type_definitions):
        """Encode a value as a string.

        This is used for an STD with variety 'union'.
        @todo Implement UnionToString"""
        raise IncompleteImplementationError('PythonSimpleTypeSupport.StringToUnion')


class AttributeDeclaration:
    VC_na = 0                   #<<< No value constraint applies
    VC_default = 1              #<<< Provided value constraint is default value
    VC_fixed = 2                #<<< Provided value constraint is fixed value

    # Value of the name attribute from the declaration
    __name = None

    # None, or a reference to a Namespace
    __targetNamespace = None
    
    __typeDefinition = None

    SCOPE_global = 'global'
    # None, the string "global", or a reference to a _ComplexTypeDefinition
    __scope = None

    # None, or a tuple containing a string followed by one of the VC_*
    # values above.
    __valueConstraint = None

    __annotation = None

    @classmethod
    def CreateBaseInstance (cls, name, target_namespace=None):
        bi = AttributeDeclaration()
        bi.__name = name
        bi.__targetNamespace = target_namespace
        return bi

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        rv = AttributeDeclaration()
        # Node should be an XMLSchema attribute node
        assert wxs.xsQualifiedName('attribute') == node.nodeName
        # TODO: Verify assumption that, because we are in a WXS element (viz., "attribute")
        # we should not have to qualify the attribute names

        # Currently only process top-level attributes
        assert wxs.xsQualifiedName('schema') == node.parentNode.nodeName

        # Implement per section 3.2.2
        rv.__name = node.getAttribute('name')
        rv.__targetNamespace = wxs.getTargetNamespace()
        rv.__scope = rv.SCOPE_global

        cn = node.getElementsByTagName('simpleType')
        assert not cn
        if node.hasAttribute('type'):
            rv.__typeDefinition = wxs.lookupSimpleType(node.getAttribute('type'))
        else:
            rv.__typeDefinition = SimpleTypeDefinition.SimpleUrTypeDefinition()

        if node.hasAttribute('default'):
            rv.__valueConstraint = (node.getAttribute('default'), rv.VC_default)
        elif node.hasAttribute('fixed'):
            rv.__valueConstraint = (node.getAttribute('fixed'), rv.VC_fixed)
        else:
            rv.__valueConstraint = None
        
        return rv


class AttributeUse:
    VC_na = AttributeDeclaration.VC_na
    VC_default = AttributeDeclaration.VC_default
    VC_fixerd = AttributeDeclaration.VC_fixed

    __required = False

    # A reference to an AttributeDeclaration
    __attributeDeclaration = None

    # None, or a tuple containing a string followed by one of the VC_*
    # values above.
    __valueConstraint = None

    
class ElementDeclaration:
    __name = None
    __targetNamespace = None
    __typeDefinition = None
    __scope = None
    __valueConstraint = None
    __nillable = False
    __identityConstraintDefinitions = None
    __substitutionGroupAffiliation = None

    SGE_none = 0
    SGE_extension = 0x01
    SGE_restriction = 0x02
    SGE_substitution = 0x04
    __substitutionGroupExclusions = SGE_none
    __disallowedSubstitutions = SGE_none

    __abstract = False
    __annotation = None
    
class Particle:
    # The minimum number of times the term may appear; defaults to 1
    __minOccurs = 1

    # If None, the term may appear any number of times; otherwise,
    # this is an integral value indicating the maximum number of times
    # the term may appear.  The default value is 1; the value, unless
    # None, must always be at least __minOccurs.
    __maxOccurs = 1

    # A reference to a particle, which is a _ModelGroup or ...
    __term = None

    
class ComplexTypeDefinition:
    # The name of the complex type, or None if the type is unnamed.
    __name = None

    # The namespace to which the type belongs
    __targetNamespace = None

    # The type resolved from the base attribute
    __baseTypeDefinition = None

    DM_none = 0                 #<<< No derivation method specified
    DM_extension = 0x01         #<<< Derivation by extension
    DM_restriction = 0x02       #<<< Derivation by restriction

    # How the type was derived
    __derivationMethod = DM_extension

    # Derived from the final and finalDefault attributes
    __final = DM_none

    # Derived from the abstract attribute
    __abstract = False
    
    __attributeUses = None
    __attributeWildcard = None

    CT_EMPTY = 0                #<<< No content
    CT_SIMPLE = 1               #<<< Simple (character) content
    CT_MIXED = 2                #<<< Children may be elements or other (e.g., character) content
    CT_ELEMENT_ONLY = 3         #<<< Expect only element content.
    __contentType = None

    # Derived from the block and blockDefault attributes
    __prohibitedSubstitutions = DM_none

    # Extracted from children of various types
    __annotations = None
    
    def __init__ (self, name, target_namespace = None):
        self.__name = name
        self.__targetNamespace = target_namespace

class AttributeGroupDefinition:
    __name = None
    __targetNamespace = None
    __attributeUses = None
    __attributeWildcard = None
    __annotation = None

class ModelGroupDefinition:
    # The name by which the model will be known in some context.
    # Derives from the name attribute of a group element)
    __name = None

    # Optional reference to a Namespace
    __targetNamespace = None

    # Reference to a _ModelGroup
    __modelGroup = None

    # Optional
    __annotation = None


class ModelGroup:
    C_INVALID = 0
    C_ALL = 0x01
    C_CHOICE = 0x02
    C_SEQUENCE = 0x03

    # One of the C_* values above
    __compositor = C_INVALID

    # A list of _Particle instances
    __particles = None

    # Optional
    __annotation = None

# 3.10.1
class Wildcard:
    __namespaceConstraint = None

    PC_INVALID = 0
    PC_skip = 0x01
    PC_lax = 0x02
    PC_strict = 0x04
    __processContents = PC_INVALID
    __annotation = None

# 3.11.1
class IdentityConstraintDefinition:
    __name = None
    __targetNamespace = None
    ICC_KEY = 0x01
    ICC_KEYREF = 0x02
    ICC_UNIQUE = 0x04
    __identityConstraintCategory = None
    __selector = None
    __fields = None
    __referencedKey = None
    __annotation = None

# 3.12.1
class NotationDeclaration:
    __name = None
    __targetNamespace = None
    __systemIdentifier = None
    __publicIdentifier = None
    __annotation = None

# 3.13.1
class Annotation:
    __applicationInformation = None
    __userInformation = None
    __attributes = None

    def __init__ (self):
        self.__applicationInformation = []
        self.__userInformation = []

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        rv = Annotation()
        # Node should be an XMLSchema annotation node
        assert wxs.xsQualifiedName('annotation') == node.nodeName
        for cn in node.childNodes:
            if wxs.xsQualifiedName('appinfo') == cn.nodeName:
                rv.__applicationInformation.append(cn)
            elif wxs.xsQualifiedName('documentation') == cn.nodeName:
                rv.__userInformation.append(cn)
            else:
                pass
        return rv

    def __str__ (self):
        text = []
        # Values in userInformation are DOM "documentation" elements.
        # We want their combined content.
        for dn in self.__userInformation:
            for cn in dn.childNodes:
                if Node.TEXT_NODE == cn.nodeType:
                    text.append(cn.data)
        return ''.join(text)


# Section 3.14.
class SimpleTypeDefinition:
    """The schema component for simple type definitions.

    This component supports the basic datatypes of XML schema, and
    those that define the values for attributes.

    @see PythonSimpleTypeSupport for additional information.
    """

    # The local name of the type
    __name = None

    # Reference to a Namespace instance to which the type belongs.
    # This should be non-None.
    __targetNamespace = None

    # Reference to the SimpleTypeDefinition on which this is based.
    # The value must be non-None except for the simple ur-type
    # definition.
    __baseTypeDefinition = None

    # @todo Support facets
    __facets = None
    # @todo Support fundamentalFacets
    __fundamentalFacets = None

    STD_empty = 0     #<<< Marker indicating an empty set of STD forms
    STD_extension = 0x01 #<<< Representation for extension in a set of STD forms
    STD_list = 0x02    #<<< Representation for list in a set of STD forms
    STD_restriction = 0x04 #<<< Representation of restriction in a set of STD forms
    STD_union = 0x08   #<<< Representation of union in a set of STD forms

    # Bitmask defining the subset that comprises the final property
    __final = STD_empty

    VARIETY_absent = 0x01       #<<< Only used for the ur-type
    VARIETY_atomic = 0x02       #<<< Use for types based on a primitive type
    VARIETY_list = 0x03         #<<< Use for lists of atomic-variety types
    VARIETY_union = 0x04        #<<< Use for types that aggregate other types

    # Identify the sort of value collection this holds
    __variety = None

    # For atomic variety only, the root (excepting ur-type) type.
    __primitiveTypeDefinition = None

    # For list variety only, the type of items in the list
    __itemTypeDefinition = None

    # For union variety only, the sequence of candidate members
    __memberTypeDefinitions = None

    # An annotation associated with the type
    __annotation = None

    # A non-property field that holds a reference to the DOM node from
    # which the type is defined.  The value is held only between the
    # point where the simple type definition instance is created until
    # the point it is resolved.
    __domNode = None
    
    # A cached reference to the schema to which this type is associated.
    __w3cXMLSchema = None

    # Allocate one of these.  Users should use one of the Create*
    # factory methods instead.  In an attempt to keep users from
    # creating these directly rather than through the approved factory
    # methods, the signature does not provide defaults for the core
    # attributes.
    def __init__ (self, name, target_namespace, variety):
        self.__name = name
        self.__targetNamespace = target_namespace
        self.__variety = variety

    def _setFromInstance (self, other):
        """Override fields in this instance with those from the other.

        This method is invoked only by Schema._addTypeDefinition, and
        then only when a built-in type collides with a schema-defined
        type.  Material like facets is not (currently) held in the
        built-in copy, so the DOM information is copied over to the
        built-in STD, which is subsequently re-resolved.
        """
        assert self.__name == other.__name
        assert self.__targetNamespace == other.__targetNamespace

        # The other STD should be an unresolved schema-defined type.
        assert other.__baseTypeDefinition is None
        assert other.__domNode is not None
        self.__domNode = other.__domNode
        assert other.__w3cXMLSchema is not None
        self.__w3cXMLSchema = other.__w3cXMLSchema

        # Mark this instance as unresolved so it is re-examined
        self.__variety = None
        return self

    def isResolved (self):
        """Indicate whether this simple type is fully defined.
        
        Type resolution for simple types means that the corresponding
        schema component fields have been set.  Specifically, that
        means variety, baseTypeDefinition, and the appropriate
        additional fields depending on variety.

        All built-in STDs are resolved upon creation.  Schema-defined
        STDs are held unresolved until the schema has been completely
        read, so that references to later schema-defined STDs can be
        resolved.  Resolution is performed after the entire schema has
        been scanned and STD instances created for all
        topLevelSimpleTypes.

        If a built-in STD is also defined in a schema (which it should
        be), the built-in STD is kept, with the schema-related
        information copied over from the matching schema-defined STD.
        The former then replaces the latter in the list of STDs to be
        resolved.  See Schema._addTypeDefinition.
        """
        # Only unresolved nodes have an unset variety
        return (self.__variety is not None)

    __SimpleUrTypeDefinition = None
    @classmethod
    def SimpleUrTypeDefinition (cls, xs_namespace=None):
        """Create the SimpleTypeDefinition instance that approximates the simple ur-type.

        See section 3.14.7.  Note that this does have to be bound to a
        provided namespace since at this point we do not have a
        namespace for XMLSchema."""

        # The first time, and only the first time, this is called, a
        # namespace should be provided which is the XMLSchema
        # namespace for this run of the system.
        if __debug__ and (xs_namespace is not None):
            assert cls.__SimpleUrTypeDefinition is None
        if cls.__SimpleUrTypeDefinition is None:
            assert xs_namespace
            bi = SimpleTypeDefinition('anySimpleType', xs_namespace, cls.VARIETY_absent)
            bi._setPythonSupport(PythonSimpleTypeSupport())

            # The baseTypeDefinition should be the actual ur-type, but the
            # instance we're creating serves as the ur-type.  So use that.
            bi.__baseTypeDefinition = bi
            # The ur-type has an absent variety, not an atomic variety, so
            # does not have a primitiveTypeDefinition

            # The ur-type is always resolved
            bi.__isResolved = True
            cls.__SimpleUrTypeDefinition = bi
        return cls.__SimpleUrTypeDefinition

    @classmethod
    def CreatePrimitiveInstance (cls, name, target_namespace, python_support):
        """Create a primitive simple type in the target namespace.

        This is mainly used to pre-load standard built-in primitive
        types, such as those defined by XMLSchema Datatypes.  You can
        use it for your own schemas as well, if you have special types
        that require explicit support to for Pythonic conversion.

        All parameters are required and must be non-None.
        """
        
        bi = SimpleTypeDefinition(name, target_namespace, cls.VARIETY_atomic)
        bi._setPythonSupport(python_support)

        # Primitive types are based on the ur-type, and have
        # themselves as their primitive type definition.
        bi.__baseTypeDefinition = cls.SimpleUrTypeDefinition()
        bi.__primitiveTypeDefinition = bi

        # Primitive types are always resolved
        bi.__isResolved = True
        return bi

    @classmethod
    def CreateDerivedInstance (cls, name, target_namespace, parent_std, python_support):
        """Create a derived simple type in the target namespace.

        This is used to pre-load standard built-in derived types.  You
        can use it for your own schemas as well, if you have special
        types that require explicit support to for Pythonic
        conversion.
        """
        assert parent_std
        assert parent_std.__variety in (cls.VARIETY_absent, cls.VARIETY_atomic)
        bi = SimpleTypeDefinition(name, target_namespace, parent_std.__variety)
        bi._setPythonSupport(python_support)

        # We were told the base type.  If this is atomic, we re-use
        # its primitive type.  Note that these all may be in different
        # namespaces.
        bi.__baseTypeDefinition = parent_std
        if cls.VARIETY_atomic == bi.__variety:
            bi.__primitiveTypeDefinition = bi.__baseTypeDefinition.__primitiveTypeDefinition

        # Derived types are always resolved
        bi.__isResolved = True
        return bi

    @classmethod
    def CreateListInstance (cls, name, target_namespace, item_std):
        """Create a list simple type in the target namespace.

        This is used to preload standard built-in list types.  You can
        use it for your own schemas as well, if you have special types
        that require explicit support to for Pythonic conversion; but
        note that such support is identified by the item_std.
        """
        bi = SimpleTypeDefinition(name, target_namespace, cls.VARIETY_list)
        # Note: The pythonSupport__ field remains None, since list
        # instances share a class-level implementation that is based
        # on their itemTypeDefinition.

        # The base type is the ur-type.  We were given the item type.
        bi.__baseTypeDefinition = cls.SimpleUrTypeDefinition()
        assert item_std
        bi.__itemTypeDefinition = item_std

        # Built-in list types are always resolved
        bi.__isResolved = True
        return bi

    @classmethod
    def CreateUnionInstance (cls, name, target_namespace, member_stds):
        """(Placeholder) Create a union simple type in the target namespace.

        This function has not been implemented."""
        raise IncompleteImplementationError('No support for built-in union types')

    def __singleSimpleTypeChild (self, wxs, body):
        simple_type_child = None
        for cn in body.childNodes:
            if (Node.ELEMENT_NODE == cn.nodeType):
                assert wxs.xsQualifiedName('simpleType') == cn.nodeName
                assert not simple_type_child
                simple_type_child = cn
        assert simple_type_child
        return simple_type_child

    # The __initializeFrom* methods are responsible for setting the
    # variety and the baseTypeDefinition.  The remainder of the
    # resolution is performed by the __completeResolution method.
    # All this stuff is from section 3.14.2.

    def __initializeFromList (self, wxs, body):
        self.__variety = self.VARIETY_list
        self.__baseTypeDefinition = self.SimpleUrTypeDefinition()
        return self.__completeResolution(wxs, body, 'list')

    def __initializeFromRestriction (self, wxs, body):
        if body.hasAttribute('base'):
            base_name = body.getAttribute('base')
            # Unless somebody's tried to resolve a restriction type
            # prior to completing scan of all topLevelSimpleType
            # elements, this only fails if the reference is to an
            # unrecognized name, which is an error in the input that
            # should produce an exception.
            self.__baseTypeDefinition = wxs.lookupSimpleType(base_name)
            # However, if the base type has been re-defined, it may
            # not yet be properly re-resolved.  Force the issue.
            # NOTE: If anybody ever defines a built-in type that uses
            # a local simple-type internally, this might cause
            # problems.  For now, it shouldn't.
            self.__baseTypeDefinition._resolve()
            assert self.__baseTypeDefinition.isResolved()
        else:
            self.__baseTypeDefinition = self.SimpleUrTypeDefinition()
        self.__variety = self.__baseTypeDefinition.__variety
        return self.__completeResolution(wxs, body, 'restriction')

    def __initializeFromUnion (self, wxs, body):
        self.__variety = self.VARIETY_union
        self.__baseTypeDefinition = self.SimpleUrTypeDefinition()
        return self.__completeResolution(wxs, body, 'union')

    # Complete the resolution of some variety of STD.  Note that the
    # variety is compounded by an alternative, since there is no
    # 'restriction' variety.
    def __completeResolution (self, wxs, body, alternative):
        assert self.__variety is not None
        if self.VARIETY_absent == self.__variety:
            # The ur-type is always resolved.  So are restrictions of it,
            # which is how we might get here.
            pass
        elif self.VARIETY_atomic == self.__variety:
            # Atomic types (and their restrictions) use the primitive
            # type, which is the highest type that is below the
            # ur-type (which is not atomic).
            ptd = self
            while self.VARIETY_atomic == ptd.__variety:
                assert ptd.__baseTypeDefinition
                ptd = ptd.__baseTypeDefinition
            self.__primitiveTypeDefinition = ptd
        elif self.VARIETY_list == self.__variety:
            if 'list' == alternative:
                if body.hasAttribute('itemType'):
                    item_type = body.getAttribute('itemType')
                    self.__itemTypeDefinition = wxs.lookupSimpleType(item_type)
                else:
                    # NOTE: The newly created anonymous item type will
                    # not be resolved; the caller needs to handle
                    # that.
                    self.__itemTypeDefinition = self.CreateFromDOM(wxs, self.__singleSimpleTypeChild(wxs, body))
            elif 'restriction' == alternative:
                self.__itemTypeDefinition = self.__baseTypeDefinition.__itemTypeDefinition
            else:
                raise LogicError('completeResolution list variety with alternative %s' % (alternative,))
        elif self.VARIETY_union == self.__variety:
            if 'union' == alternative:
                mtd = []
                # TODO If present, need to extract names from memberTypes
                if body.hasAttribute(wxs.xsQualifiedName('memberTypes')):
                    raise IncompleteImplementationError('union needs to extract names from memberTypes')
                # NOTE: Newly created anonymous types need to be resolved
                for cn in body.childNodes:
                    if (Node.ELEMENT_NODE == cn.nodeType):
                        if wxs.xsQualifiedName('simpleType') == cn.nodeName:
                            mtd.append(self.CreateFromDOM(wxs, cn))
            elif 'restriction' == alternative:
                assert self.__baseTypeDefinition__
                # If this fails, it's probably a use-before-def issue in the schema
                assert self.__baseTypeDefinition__.isResolved()
                mtd = self.__baseTypeDefinition.__memberTypeDefinitions
                assert mtd is not None
            else:
                raise LogicError('completeResolution union variety with alternative %s' % (alternative,))
            # Save a unique copy
            self.__memberTypeDefinitions = mtd[:]
        else:
            print 'VARIETY "%s"' % (self.__variety,)
            raise LogicError('completeResolution with variety 0x%02x' % (self.__variety,))
        self.__isResolved = True
        return self

    def _resolve (self):
        # Beware: there is a slight issue here because we use variety,
        # which is set in the initialize* method, to indicate that the
        # node has been resolved, but resolution is not fully complete
        # until the completeResolution invocation is done.  During
        # that period, checking for resolution may prematurely
        # succeed.  This should not be an issue because in the current
        # implementation resolution will succeed, and it's already in
        # progress.  Only for restrictions is resolution potentially
        # recursive.
        if self.__variety is not None:
            return self
        assert self.__domNode
        node = self.__domNode
        wxs = self.__w3cXMLSchema
        assert wxs is not None
        
        elt_map = {}
        for t in [ 'list', 'restriction', 'union' ]:
            qn = wxs.xsQualifiedName(t)
            elt_map[t] = [ _cn for _cn in node.childNodes if _cn.nodeName == qn ]

        # The guts of the node should be exactly one instance of
        # exactly one of these three types.
        elts = elt_map['list']
        if elts:
            assert 1 == len(elts), '%s has multiple list elements' % (name,)
            self.__initializeFromList(wxs, elts[0])
            
        elts = elt_map['restriction']
        if elts:
            assert not self.isResolved()
            assert 1 == len(elts), '%s has multiple restriction elements' % (name,)
            self.__initializeFromRestriction(wxs, elts[0])

        elts = elt_map['union']
        if elts:
            assert not self.isResolved()
            assert 1 == len(elts), '%s has multiple union elements' % (name,)
            self.__initializeFromUnion(wxs, elts[0])

        assert self.__variety is not None
        return self

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        # Node should be an XMLSchema simpleType node
        assert wxs.xsQualifiedName('simpleType') == node.nodeName

        # TODO: Need to see what a "final" attribute looks like
        assert not node.hasAttribute('final')

        name = None
        if node.hasAttribute('name'):
            name = node.getAttribute('name')

        rv = SimpleTypeDefinition(name, wxs.getTargetNamespace(), None)
        rv.__domNode = node
        rv.__w3cXMLSchema = wxs

        # Creation does not attempt to do resolution.  Queue up the newly created
        # whatsis so we can resolve it after everything's been read in.
        wxs._addUnresolvedSimpleTypeDefinition(rv)
        
        return rv

    # pythonSupport is an instance of a subclass of
    # PythonSimpleTypeSupport.  When set, this simple type definition
    # must be associated with the support instance.
    __pythonSupport = None

    def _setPythonSupport (self, python_support):
        # Includes check that python_support is not None
        assert isinstance(python_support, PythonSimpleTypeSupport)
        # Can't share support instances
        self.__pythonSupport = python_support
        self.__pythonSupport._setSimpleTypeDefinition(self)
        return self.__pythonSupport

    def localName (self):
        return self.__name

    def name (self):
        if self.__name is not None:
            if self.__targetNamespace:
                return self.__targetNamespace.qualifiedName(self.__name)
        return self.__name

    def pythonSupport (self):
        if self.__pythonSupport is None:
            raise LogicError('%s: No support defined' % (self.name(),))
        return self.__pythonSupport

    def stringToPython (self, string):
        return self.pythonSupport().stringToPython(string)

    def pythonToString (self, value):
        return self.pythonSupport().pythonToString(value)

class Schema:
    __typeDefinitions = None
    __attributeDeclarations = None
    __elementDeclarations = None
    __attributeGroupDefinitions = None
    __modelGroupDefinitions = None
    __notationDeclarations = None
    __annotations = None

    __unresolvedSimpleTypeDefinitions = None

    def __init__ (self):
        self.__annotations = [ ]
        self.__typeDefinitions = { }
        self.__unresolvedSimpleTypeDefinitions = []

    def _addUnresolvedSimpleTypeDefinition (self, std):
        """Invoked by SimpleTypeDefinition component when creating a
        non-builtin simple type in this schema.

        Be aware that the type may not have a name: this method is
        invoked during resolution when evaluating localSimpleTypes"""
        self.__unresolvedSimpleTypeDefinitions.append(std)
        return std

    def __replaceUnresolvedSimpleTypeDefinition (self, unresolved_std, replacement_std):
        assert unresolved_std in self.__unresolvedSimpleTypeDefinitions
        self.__unresolvedSimpleTypeDefinitions.remove(unresolved_std)
        assert replacement_std not in self.__unresolvedSimpleTypeDefinitions
        self.__unresolvedSimpleTypeDefinitions.append(replacement_std)

    def _resolveSimpleTypeDefinitions (self):
        # @todo Need to top-sort the type definitions so we don't try
        # to do a restriction on a restriction that hasn't been
        # resolved.  For now, assume whoever wrote the schema was kind
        # enough not to use before definition.  Which isn't going to
        # be true.
        while self.__unresolvedSimpleTypeDefinitions:
            # Save the list of unresolved STDs, then prepare for any
            # new STDs defined during resolution.  They'll have to be
            # localSimpleTypes, not named, so resolution shouldn't
            # fail, but we still need to process them.
            unresolved = self.__unresolvedSimpleTypeDefinitions
            self.__unresolvedSimpleTypeDefinitions = []
            for std in unresolved:
                std._resolve()
                assert std.isResolved()
        self.__unresolvedSimpleTypeDefinitions = None
        return self

    def _addAnnotation (self, annotation):

        self.__annotations.append(annotation)
        return annotation

    def _addTypeDefinition (self, definition):
        assert isinstance(definition, (SimpleTypeDefinition, ComplexTypeDefinition))
        local_name = definition.localName()
        assert 0 > local_name.find(':')
        assert definition
        old_definition = self.__typeDefinitions.get(local_name, None)
        if old_definition is not None:
            # Copy schema-related information from the new definition
            # into the old one, and continue to use the old one.
            self.__replaceUnresolvedSimpleTypeDefinition(definition, old_definition)
            definition = old_definition._setFromInstance(definition)
        else:
            self.__typeDefinitions[local_name] = definition
        return definition
    
    def _lookupTypeDefinition (self, local_name):
        return self.__typeDefinitions.get(local_name, None)
    
    def _typeDefinitions (self):
        return self.__typeDefinitions.values()
