##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Package wrapper for Document Template

This wrapper allows the (now many) document template modules to be
segregated in a separate package.

$Id: __init__.py,v 1.1 2004/07/27 02:42:53 zworkb Exp $
"""

from zope.documenttemplate.documenttemplate import String, HTML
from zope.documenttemplate.documenttemplate import html_quote
