##########################################################################
#  
#  Copyright (c) 2013, Image Engine Design Inc. All rights reserved.
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
#      * Neither the name of Image Engine Design nor the names of
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

import unittest

import IECore
import Gaffer
import GafferImage
import os

class SamplerTest( unittest.TestCase ) :
	
	fileName = os.path.expandvars( "$GAFFER_ROOT/python/GafferTest/images/checker.exr" )

	def testOutOfBoundsSampleModeBlack( self ) : 
		
		s = Gaffer.ScriptNode()
		r = GafferImage.ImageReader()
		r["fileName"].setValue( self.fileName )		
		s.addChild( r )
			
		c = Gaffer.Context()
		c["image:channelName"] = 'R'
		c["image:tileOrigin"] = IECore.V2i( 0 )
		
		bounds = r["out"]["dataWindow"].getValue();
		f = GafferImage.Filter.create( "Box" )
	
		testCases = [
			( bounds.min.x-1, bounds.min.y ),
			( bounds.min.x, bounds.min.y-1 ),
			( bounds.max.x, bounds.max.y+1 ),
			( bounds.max.x+1, bounds.max.y ),
			( bounds.min.x-1, bounds.max.y ),
			( bounds.min.x, bounds.max.y+1 ),
			( bounds.max.x+1, bounds.min.y ),
			( bounds.max.x, bounds.min.y-1 )
		]

		self.assertTrue( "Box" in GafferImage.Filter.filters() )
		f = GafferImage.Filter.create("Box")
		
		with c :
			
			self.assertTrue( "R" in r["out"]["channelNames"].getValue() )
			s = GafferImage.Sampler( r["out"], "R", bounds, GafferImage.BoundingMode.Black )
				
			# Check that the bounding pixels are non zero.
			self.assertNotEqual( s.sample( bounds.min.x+.5, bounds.min.y+.5, f ), 0. )
			self.assertNotEqual( s.sample( bounds.max.x+.5, bounds.max.y+.5, f ), 0. )
			self.assertNotEqual( s.sample( bounds.min.x+.5, bounds.max.y+.5, f ), 0. )
			self.assertNotEqual( s.sample( bounds.max.x+.5, bounds.min.y+.5, f ), 0. )
	
			# Sample out of bounds and assert that a zero is returned.	
			for x, y in testCases :
				self.assertEqual( s.sample( x+.5, y+.5, f ), 0. )

	def testOutOfBoundsSampleModeClamp( self ) : 
		
		s = Gaffer.ScriptNode()
		r = GafferImage.ImageReader()
		r["fileName"].setValue( self.fileName )		
		s.addChild( r )
			
		c = Gaffer.Context()
		c["image:channelName"] = 'R'
		c["image:tileOrigin"] = IECore.V2i( 0 )
		
		bounds = r["out"]["dataWindow"].getValue();
		f = GafferImage.Filter.create( "Box" )
	
		with c :
			
			self.assertTrue( "R" in r["out"]["channelNames"].getValue() )
			s = GafferImage.Sampler( r["out"], "R", bounds, GafferImage.BoundingMode.Clamp )
		
			# Get the values of the corner pixels.
			bl = s.sample( bounds.min.x+.5, bounds.min.y+.5, f )
			br = s.sample( bounds.max.x+.5, bounds.min.y+.5, f )
			tr = s.sample( bounds.max.x+.5, bounds.max.y+.5, f )
			tl = s.sample( bounds.min.x+.5, bounds.max.y+.5, f )
	
			# Sample out of bounds and assert that the same value as the nearest pixel is returned.	
			self.assertEqual( s.sample( bounds.min.x-1, bounds.min.y, f ), bl )
			self.assertEqual( s.sample( bounds.min.x, bounds.min.y-1, f ), bl )
			self.assertEqual( s.sample( bounds.max.x, bounds.max.y+1, f ), tr )
			self.assertEqual( s.sample( bounds.max.x+1, bounds.max.y, f ), tr )
			self.assertEqual( s.sample( bounds.min.x-1, bounds.max.y, f ), tl )
			self.assertEqual( s.sample( bounds.min.x, bounds.max.y+1, f ), tl )
			self.assertEqual( s.sample( bounds.max.x+1, bounds.min.y, f ), br )
			self.assertEqual( s.sample( bounds.max.x, bounds.min.y-1, f ), br )
	
	# Test that the hash() method accumulates all of the hashes of the tiles within the sample area
	# for a large number of different sample areas.
	def testSampleHash( self ) :
		
		s = Gaffer.ScriptNode()
		r = GafferImage.ImageReader()
		r["fileName"].setValue( self.fileName )		
		s.addChild( r )
		
		tileSize = GafferImage.ImagePlug.tileSize() 
		# Test one tile first.
		
		for w in range(2, 6) :
			for x in range(-3, 3) :
				for y in range(-3, 3) :
					sampleBox = IECore.Box2i( IECore.V2i( x*tileSize, y*tileSize ), IECore.V2i( x*tileSize+w*tileSize/2, y*tileSize+w*tileSize/2 ) )
					self.__testHashOfBounds( sampleBox, "R", r["out"] )
						

	# A private method that acumulates the hashes of the tiles within
	# a box and compares them to the hash returned by the sampler.
	def __testHashOfBounds( self, box, channel, plug ) :
		
		tileOrigin = GafferImage.ImagePlug.tileOrigin( IECore.V2i( box.min ) )
		self.assertTrue( channel in plug["channelNames"].getValue() )
			
		c = Gaffer.Context()
		c["image:channelName"] = channel
		c["image:tileOrigin"] = tileOrigin

		h = IECore.MurmurHash()
		h2 = h

		# Get the hash from the sampler.
		with c :		
			s = GafferImage.Sampler( plug, channel, box, GafferImage.BoundingMode.Clamp )
			s.hash( h )

		# Get the hash from the tiles within our desired sample area.
		with c :		
			y = box.min.y
			while y <= box.max.y :
				x = box.min.x
				while x <= box.max.x :
					tileOrigin = GafferImage.ImagePlug.tileOrigin( IECore.V2i( x, y ) )
					tile = IECore.Box2i( tileOrigin, tileOrigin + IECore.V2i( GafferImage.ImagePlug.tileSize()-1 ) )
					h2.append( plug.channelDataHash( channel, tileOrigin ) )
					x += GafferImage.ImagePlug.tileSize()	
				y += GafferImage.ImagePlug.tileSize()	
		
		self.assertEqual( h, h2 )

