## Script (Python) "check_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None,required=0,alternative_id=None,contained_by=None
##title=Check an id's validity
#
# Test an id to make sure it is valid.
#
# Returns an error message if the id is bad or None if the id is good.
#
# id - the id to check
# required - if required is 1, makes sure a suitable id has been supplied
# alternative_id - an alternative value to use for the id if the id is empty or autogenerated
#
# Note: the error messages here might cause some i18n headaches because they
# include the actual id.  The reason the id is included is to handle id error
# messages for such objects as files and images that supply an alternative id
# when an id is autogenerated.  If you say "There is already an item with this name
# in this folder" for an image that has the Name field populated with an autogenerated
# id, it can cause some confusion, since the real problem is the name of the image
# file name, not in the name of the autogenerated id.

from AccessControl import Unauthorized

# if an alternative id has been supplied, see if we need to use it
if alternative_id and not id:
#if alternative_id and (not id or context.isIDAutoGenerated(id)):
    id = alternative_id

# make sure we have an id if one is required
if not id:
    if required:
        return 'Please enter a name.'
    # id is not required, no alternative specified, so assume object's id will be
    # context.getId().  We still should check to make sure context.getId() is OK to
    # handle the case of pre-created objects constructed via portal_factory.  The
    # main potential problem is an id collision, e.g. if portal_factory autogenerates
    # an id that already exists.
    id = context.getId()

# do basic id validation
if not context.plone_utils.good_id(id):
    # id is bad so lets find the bad chars
    c = context.plone_utils.bad_chars(id)
    return '\'%s\' is not a legal name. '\
     'The following characters are invalid: %s'\
     % (id, " ".join(c))

# check for a catalog index
if id in context.portal_catalog.indexes():
    return '\'%s\' is reserved.' % id

# id is good; make sure we have no id collisions
if context.portal_factory.isTemporary(context):
    # always check for collisions if we are creating a new object
    checkForCollision = 1
else:
    # if we have an existing object, only check for collisions if we are changing the id
    checkForCollision = (context.getId() != id)

# perform the actual check
if checkForCollision:
    # handles two use cases:
    # 1. object has not yet been created and we don't know where it will be
    # 2. object has been created and checking validity of id within container
    if not contained_by:
        contained_by = context.getParentNode()

    if hasattr(contained_by, 'objectIds'):
        try:
            if id in contained_by.objectIds():
                return 'There is already an item named \'%s\' in this folder.' % id
        except Unauthorized:
            pass  # ignore if we don't have permission
    if hasattr(contained_by, 'checkIdAvailable'):
        try:
            if not contained_by.checkIdAvailable(id):
                return '\'%s\' is reserved.' % id
            else:
                return
        except Unauthorized:
            pass # ignore if we don't have permission
    if hasattr(contained_by, 'checkValidId'):
        try:
            contained_by.checkValidId(id)
        except BadRequestException:
            return '\'%s\' is reserved.' % id
