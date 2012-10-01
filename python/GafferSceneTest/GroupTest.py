##########################################################################
#  
#  Copyright (c) 2012, John Haddon. All rights reserved.
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

import unittest
import threading

import IECore

import Gaffer
import GafferScene
import GafferSceneTest

class GroupTest( GafferSceneTest.SceneTestCase ) :
		
	def testTwoLevels( self ) :
	
		sphere = IECore.SpherePrimitive()
		input = GafferSceneTest.CompoundObjectSource()
		input["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( sphere.bound() ),
				"children" : {
					"group" : {
						"bound" : IECore.Box3fData( sphere.bound() ),
						"children" : {
							"sphere" : {
								"bound" : IECore.Box3fData( sphere.bound() ),
								"object" : sphere,
							},
						},
					},
				},
			} ),
		)
		
		group = GafferScene.Group( inputs = { "in" : input["out"], "name" : "topLevel" } )
		self.assertEqual( group["name"].getValue(), "topLevel" )
		
		self.assertEqual( group["out"].object( "/" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/" ), IECore.StringVectorData( [ "topLevel" ] ) )

		self.assertEqual( group["out"].object( "/topLevel" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/topLevel" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel" ), IECore.StringVectorData( [ "group" ] ) )
		
		self.assertEqual( group["out"].object( "/topLevel/group" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/topLevel/group" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/group" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/group" ), IECore.StringVectorData( [ "sphere" ] ) )
		
		self.assertEqual( group["out"].object( "/topLevel/group/sphere" ), sphere )
		self.assertEqual( group["out"].transform( "/topLevel/group/sphere" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/group/sphere" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/group/sphere" ), IECore.StringVectorData() )
	
	def testTransform( self ) :
	
		sphere = IECore.SpherePrimitive()
		originalRootBound = sphere.bound()
		originalRootBound.min += IECore.V3f( 1, 0, 0 )
		originalRootBound.max += IECore.V3f( 1, 0, 0 )
		input = GafferSceneTest.CompoundObjectSource()
		input["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( originalRootBound ),
				"children" : {
					"sphere" : {
						"object" : sphere,
						"bound" : IECore.Box3fData( sphere.bound() ),
						"transform" : IECore.M44fData( IECore.M44f.createTranslated( IECore.V3f( 1, 0, 0 ) ) ),
					}
				}
			} )
		)
		
		group = GafferScene.Group( inputs = { "in" : input["out"], "transform.translate" : IECore.V3f( 0, 1, 0 ) } )
		self.assertEqual( group["name"].getValue(), "group" )
		
		groupedRootBound = IECore.Box3f( originalRootBound.min, originalRootBound.max )
		groupedRootBound.min += IECore.V3f( 0, 1, 0 )
		groupedRootBound.max += IECore.V3f( 0, 1, 0 )
		
		self.assertEqual( group["out"].object( "/" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/" ), groupedRootBound )
		self.assertEqual( group["out"].childNames( "/" ), IECore.StringVectorData( [ "group" ] ) )
		
		self.assertEqual( group["out"].object( "/group" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/group" ), IECore.M44f.createTranslated( IECore.V3f( 0, 1, 0 ) ) )
		self.assertEqual( group["out"].bound( "/group" ), originalRootBound )
		self.assertEqual( group["out"].childNames( "/group" ), IECore.StringVectorData( [ "sphere" ] ) )
	
		self.assertEqual( group["out"].object( "/group/sphere" ), sphere )
		self.assertEqual( group["out"].transform( "/group/sphere" ), IECore.M44f.createTranslated( IECore.V3f( 1, 0, 0 ) ) )
		self.assertEqual( group["out"].bound( "/group/sphere" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/group/sphere" ), IECore.StringVectorData() )
	
	def testAddAndRemoveInputs( self ) :
	
		g = GafferScene.Group()
		p = GafferScene.Plane()
		
		def scenePlugNames() :
			return [ plug.getName() for plug in g.children() if isinstance( plug, GafferScene.ScenePlug ) and plug.direction() == Gaffer.Plug.Direction.In ]
		
		self.assertEqual( scenePlugNames(), [ "in"] )
		
		g["in"].setInput( p["out"] )
		self.assertEqual( scenePlugNames(), [ "in", "in1"] )
		
 		g["in1"].setInput( p["out"] )
 		self.assertEqual( scenePlugNames(), [ "in", "in1", "in2" ] )

 		g["in1"].setInput( None )
 		self.assertEqual( scenePlugNames(), [ "in", "in1" ] )

 		g["in"].setInput( None )
 		self.assertEqual( scenePlugNames(), [ "in" ] )

 		g["in"].setInput( p["out"] )
 		self.assertEqual( scenePlugNames(), [ "in", "in1"] )

 		g["in1"].setInput( p["out"] )
 		self.assertEqual( scenePlugNames(), [ "in", "in1", "in2" ] )

		g["in"].setInput( None )
		self.assertEqual( scenePlugNames(), [ "in", "in1", "in2" ] )
		
	def testMerge( self ) :
	
		sphere = IECore.SpherePrimitive()
		input1 = GafferSceneTest.CompoundObjectSource()
		input1["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( sphere.bound() ),
				"children" : {
					"sphereGroup" : {
						"bound" : IECore.Box3fData( sphere.bound() ),
						"children" : {
							"sphere" : {
								"bound" : IECore.Box3fData( sphere.bound() ),
								"object" : sphere,
							},
						},
					},
				},
			} ),
		)
		
		plane = IECore.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		input2 = GafferSceneTest.CompoundObjectSource()
		input2["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( plane.bound() ),
				"children" : {
					"planeGroup" : {
						"bound" : IECore.Box3fData( plane.bound() ),
						"children" : {
							"plane" : {
								"bound" : IECore.Box3fData( plane.bound() ),
								"object" : plane,
							},
						},
					},
				},
			} ),
		)
		
		combinedBound = sphere.bound()
		combinedBound.extendBy( plane.bound() )
		
		group = GafferScene.Group()
		group["name"].setValue( "topLevel" )
		group["in"].setInput( input1["out"] )
		group["in1"].setInput( input2["out"] )
				
		self.assertEqual( group["out"].object( "/" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/" ), combinedBound )
		self.assertEqual( group["out"].childNames( "/" ), IECore.StringVectorData( [ "topLevel" ] ) )

		self.assertEqual( group["out"].object( "/topLevel" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/topLevel" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel" ), combinedBound )
		self.assertEqual( group["out"].childNames( "/topLevel" ), IECore.StringVectorData( [ "sphereGroup", "planeGroup" ] ) )
		
		self.assertEqual( group["out"].object( "/topLevel/sphereGroup" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/topLevel/sphereGroup" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/sphereGroup" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/sphereGroup" ), IECore.StringVectorData( [ "sphere" ] ) )
		
		self.assertEqual( group["out"].object( "/topLevel/sphereGroup/sphere" ), sphere )
		self.assertEqual( group["out"].transform( "/topLevel/sphereGroup/sphere" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/sphereGroup/sphere" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/sphereGroup/sphere" ), IECore.StringVectorData() )
		
		self.assertEqual( group["out"].object( "/topLevel/planeGroup" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/topLevel/planeGroup" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/planeGroup" ), plane.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/planeGroup" ), IECore.StringVectorData( [ "plane" ] ) )
		
		self.assertEqual( group["out"].object( "/topLevel/planeGroup/plane" ), plane )
		self.assertEqual( group["out"].transform( "/topLevel/planeGroup/plane" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/planeGroup/plane" ), plane.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/planeGroup/plane" ), IECore.StringVectorData() )
	
	def testNameClashes( self ) :
	
		sphere = IECore.SpherePrimitive()
		input1 = GafferSceneTest.CompoundObjectSource()
		input1["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( sphere.bound() ),
				"children" : {
					"myLovelyObject" : {
						"bound" : IECore.Box3fData( sphere.bound() ),
						"object" : sphere,
					},
				},
			} ),
		)
		
		plane = IECore.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		input2 = GafferSceneTest.CompoundObjectSource()
		input2["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( plane.bound() ),
				"children" : {
					"myLovelyObject" : {
						"bound" : IECore.Box3fData( plane.bound() ),
						"object" : plane,
					},
				},
			} ),
		)
		
		combinedBound = sphere.bound()
		combinedBound.extendBy( plane.bound() )
		
		group = GafferScene.Group()
		group["name"].setValue( "topLevel" )
		group["in"].setInput( input1["out"] )
		group["in1"].setInput( input2["out"] )
				
		self.assertEqual( group["out"].object( "/" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/" ), combinedBound )
		self.assertEqual( group["out"].childNames( "/" ), IECore.StringVectorData( [ "topLevel" ] ) )

		self.assertEqual( group["out"].object( "/topLevel" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/topLevel" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel" ), combinedBound )
		self.assertEqual( group["out"].childNames( "/topLevel" ), IECore.StringVectorData( [ "myLovelyObject", "myLovelyObject1" ] ) )
		
		self.assertEqual( group["out"].object( "/topLevel/myLovelyObject" ), sphere )
		self.assertEqual( group["out"].transform( "/topLevel/myLovelyObject" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/myLovelyObject" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/myLovelyObject" ), IECore.StringVectorData() )
		
		self.assertEqual( group["out"].object( "/topLevel/myLovelyObject1" ), plane )
		self.assertEqual( group["out"].transform( "/topLevel/myLovelyObject1" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/myLovelyObject1" ), plane.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/myLovelyObject1" ), IECore.StringVectorData() )
	
	def testSerialisationOfDynamicInputs( self ) :
	
		s = Gaffer.ScriptNode()
		s["c"] = GafferScene.Camera()
		s["g"] = GafferScene.Group()
		s["g"]["in"].setInput( s["c"]["out"] )
		s["g"]["in1"].setInput( s["c"]["out"] )
		
		self.failUnless( "in2" in s["g"] )
		self.assertEqual( s["g"]["in2"].getInput(), None )
		
		ss = s.serialise()
				
		s = Gaffer.ScriptNode()
		s.execute( ss )
		
		self.failUnless( s["g"]["in"].getInput().isSame( s["c"]["out"] ) )
		self.failUnless( s["g"]["in1"].getInput().isSame( s["c"]["out"] ) )
		self.failUnless( "in2" in s["g"] )
		self.assertEqual( s["g"]["in2"].getInput(), None )
	
	def testNameClashesWithNumericSuffixes( self ) :
	
		sphere = IECore.SpherePrimitive()
		input1 = GafferSceneTest.CompoundObjectSource()
		input1["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( sphere.bound() ),
				"children" : {
					"myLovelyObject1" : {
						"bound" : IECore.Box3fData( sphere.bound() ),
						"object" : sphere,
					},
				},
			} ),
		)
		
		plane = IECore.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		input2 = GafferSceneTest.CompoundObjectSource()
		input2["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( plane.bound() ),
				"children" : {
					"myLovelyObject1" : {
						"bound" : IECore.Box3fData( plane.bound() ),
						"object" : plane,
					},
				},
			} ),
		)
		
		combinedBound = sphere.bound()
		combinedBound.extendBy( plane.bound() )
		
		group = GafferScene.Group()
		group["name"].setValue( "topLevel" )
		group["in"].setInput( input1["out"] )
		group["in1"].setInput( input2["out"] )
				
		self.assertEqual( group["out"].object( "/" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/" ), combinedBound )
		self.assertEqual( group["out"].childNames( "/" ), IECore.StringVectorData( [ "topLevel" ] ) )

		self.assertEqual( group["out"].object( "/topLevel" ), IECore.NullObject() )
		self.assertEqual( group["out"].transform( "/topLevel" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel" ), combinedBound )
		self.assertEqual( group["out"].childNames( "/topLevel" ), IECore.StringVectorData( [ "myLovelyObject1", "myLovelyObject2" ] ) )
		
		self.assertEqual( group["out"].object( "/topLevel/myLovelyObject1" ), sphere )
		self.assertEqual( group["out"].transform( "/topLevel/myLovelyObject1" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/myLovelyObject1" ), sphere.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/myLovelyObject1" ), IECore.StringVectorData() )
		
		self.assertEqual( group["out"].object( "/topLevel/myLovelyObject2" ), plane )
		self.assertEqual( group["out"].transform( "/topLevel/myLovelyObject2" ), IECore.M44f() )
		self.assertEqual( group["out"].bound( "/topLevel/myLovelyObject2" ), plane.bound() )
		self.assertEqual( group["out"].childNames( "/topLevel/myLovelyObject2" ), IECore.StringVectorData() )
	
	def testNameClashesWithThreading( self ) :
	
		sphere = IECore.SpherePrimitive()
		input1 = GafferSceneTest.CompoundObjectSource()
		input1["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( sphere.bound() ),
				"children" : {
					"myLovelyObject1" : {
						"bound" : IECore.Box3fData( sphere.bound() ),
						"object" : sphere,
					},
				},
			} ),
		)
		
		plane = IECore.MeshPrimitive.createPlane( IECore.Box2f( IECore.V2f( -1 ), IECore.V2f( 1 ) ) )
		input2 = GafferSceneTest.CompoundObjectSource()
		input2["in"].setValue(
			IECore.CompoundObject( {
				"bound" : IECore.Box3fData( plane.bound() ),
				"children" : {
					"myLovelyObject1" : {
						"bound" : IECore.Box3fData( plane.bound() ),
						"object" : plane,
					},
				},
			} ),
		)
		
		group = GafferScene.Group()
		group["name"].setValue( "topLevel" )
		group["in"].setInput( input1["out"] )
		group["in1"].setInput( input2["out"] )
		
		sceneProcedural = GafferScene.SceneProcedural( group["out"], Gaffer.Context(), "/" )
		
		for i in range( 0, 1000 ) :
			mh = IECore.CapturingMessageHandler()
			with mh :
				# we use a CapturingRenderer as it will invoke the procedural
				# on multiple threads for us automatically.
				renderer = IECore.CapturingRenderer()
				with IECore.WorldBlock( renderer ) :
					renderer.procedural( sceneProcedural )
			self.assertEqual( len( mh.messages ), 0 )
	
	def testHashes( self ) :
	
		p = GafferScene.Plane()
		
		g = GafferScene.Group()
		g["in"].setInput( p["out"] )

		self.assertSceneValid( g["out"] )
		self.assertSceneHashesEqual( g["out"], p["out"], childPlugNames = ( "globals", ) )
	
		self.assertPathHashesEqual( g["out"], "/group/plane", p["out"], "/plane" )
	
 	def testTransformHash( self ) :

		p = GafferScene.Plane()
		
		g1 = GafferScene.Group()
		g1["in"].setInput( p["out"] )

		g2 = GafferScene.Group()
 		g2["in"].setInput( p["out"] )
 		
 		self.assertSceneHashesEqual( g1["out"], g2["out"] )
 		
	 	g2["transform"]["translate"].setValue( IECore.V3f( 1, 0, 0 ) )
	 		 	
 		self.assertSceneHashesEqual( g1["out"], g2["out"], pathsToIgnore = ( "/", "/group", ) )
 		self.assertSceneHashesEqual( g1["out"], g2["out"], childPlugNamesToIgnore = ( "transform", "bound" ) )
		self.assertNotEqual( g1["out"].transformHash( "/group" ), g2["out"].transformHash( "/group" ) )
		self.assertEqual( g1["out"].boundHash( "/group" ), g2["out"].boundHash( "/group" ) )
		self.assertNotEqual( g1["out"].boundHash( "/" ), g2["out"].boundHash( "/" ) )
		
	def testChildNamesHash( self ) :
	
		p = GafferScene.Plane()
		
		g1 = GafferScene.Group()
		g1["in"].setInput( p["out"] )
		
		g2 = GafferScene.Group()
 		g2["in"].setInput( p["out"] )
 		
 		self.assertSceneHashesEqual( g1["out"], g2["out"] )

		g2["name"].setValue( "stuff" )
		
		equivalentPaths = [ 
			( "/", "/" ),
			( "/group", "/stuff" ),
			( "/group/plane", "/stuff/plane" ),
		]
		for path1, path2 in equivalentPaths :
			self.assertEqual( g1["out"].boundHash( path1 ), g2["out"].boundHash( path2 ) )
			self.assertEqual( g1["out"].transformHash( path1 ), g2["out"].transformHash( path2 ) )
			self.assertEqual( g1["out"].objectHash( path1 ), g2["out"].objectHash( path2 ) )
			self.assertEqual( g1["out"].attributesHash( path1 ), g2["out"].attributesHash( path2 ) )
			if path1 is not "/" :
				self.assertEqual( g1["out"].childNamesHash( path1 ), g2["out"].childNamesHash( path2 ) )
			else :
				self.assertNotEqual( g1["out"].childNamesHash( path1 ), g2["out"].childNamesHash( path2 ) )
		 		
if __name__ == "__main__":
	unittest.main()
