##########################################################################
#
#  Copyright (c) 2014, Esteban Tovagliari. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import IECore

import Gaffer
import GafferUI
import GafferAppleseed

Gaffer.Metadata.registerNode(

	GafferAppleseed.AppleseedRender,

	"description",
	"""
	Performs offline batch rendering using the
	appleseed renderer. This is done in two phases -
	first the scene geometry is exported to mesh files and an appleseed project
	is generated, and then appleseed is invoked to render it.
	""",

	plugs = {

		"mode" : [

			"description",
			"""
			When in the standard "Render" mode, an appleseed project
			is generated and then renderered in appleseed.
			Alternatively, just the appleseed project can be generated
			and then another method can be used to post-process
			it or launch the render - a SystemCommand node may
			be useful for this.
			""",

			"preset:Render", "render",
			"preset:Generate .appleseed only", "generate",

			"nodule:type", "",
			"plugValueWidget:type", "GafferUI.PresetsPlugValueWidget",

		],

		"fileName" : [

			"description",
			"""
			The name of the appleseed project file to be generated.
			""",

			"nodule:type", "",
			"plugValueWidget:type", "GafferUI.FileSystemPathPlugValueWidget",
			"pathPlugValueWidget:leaf", True,
			"pathPlugValueWidget:bookmarks", "appleseed",
			"fileSystemPathPlugValueWidget:extensions", IECore.StringVectorData( [ "appleseed" ] ),

		],

		"verbosity" : [

			"description",
			"""
			Controls the verbosity of the appleseed renderer output.
			""",

			"preset:Fatal", "fatal",
			"preset:Error", "error",
			"preset:Warning", "warning",
			"preset:Debug", "debug",
			"preset:Info", "info",

			"nodule:type", "",
			"plugValueWidget:type", "GafferUI.PresetsPlugValueWidget",

		],

	}

)
