//////////////////////////////////////////////////////////////////////////
//  
//  Copyright (c) 2012, John Haddon. All rights reserved.
//  
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//  
//      * Redistributions of source code must retain the above
//        copyright notice, this list of conditions and the following
//        disclaimer.
//  
//      * Redistributions in binary form must reproduce the above
//        copyright notice, this list of conditions and the following
//        disclaimer in the documentation and/or other materials provided with
//        the distribution.
//  
//      * Neither the name of John Haddon nor the names of
//        any other contributors to this software may be used to endorse or
//        promote products derived from this software without specific prior
//        written permission.
//  
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//  
//////////////////////////////////////////////////////////////////////////

#ifndef GAFFERUI_GRAPHLAYOUT_H
#define GAFFERUI_GRAPHLAYOUT_H

#include "IECore/RunTimeTyped.h"

#include "GafferUI/TypeIds.h"

namespace Gaffer
{

IE_CORE_FORWARDDECLARE( Node )
IE_CORE_FORWARDDECLARE( Set )

} // namespace Gaffer

namespace GafferUI
{

IE_CORE_FORWARDDECLARE( GraphGadget );

/// The GraphLayout class provides a base class for implementing layout algorithms for
/// the GraphGadget. This simplifies GraphGadget implementation and makes it possible to
/// implement different styles of layout for different scenarios.
/// \todo This needs a method for laying out a whole bunch of nodes at once, and perhaps
/// a mechanism of named operations which can be invoked by menu items in the GraphEditor.
/// The StandardGraphLayout should then implement some variation of the Sugiyama algorithm
/// and have named operations for snapping to grid, aligning etc.
class GraphLayout : public IECore::RunTimeTyped
{

	public :

		virtual ~GraphLayout();

		IE_CORE_DECLARERUNTIMETYPEDEXTENSION( GraphLayout, GraphLayoutTypeId, IECore::RunTimeTyped );

		/// Attempts to connect the specified node to the specified input nodes. Returns true
		/// if any connections were made and false otherwise.
		virtual bool connectNode( GraphGadget *graph, Gaffer::Node *node, Gaffer::Set *potentialInputs ) const = 0;
		/// Positions the specified node somewhere sensible, while leaving all other
		/// nodes in the graph in their current positions. Returns true if positioning was successful
		/// and false otherwise.
		virtual bool positionNode( GraphGadget *graph, Gaffer::Node *node ) const = 0;		

	protected :
	
		GraphLayout();		
			
};

IE_CORE_DECLAREPTR( GraphLayout );

} // namespace GafferUI

#endif // GAFFERUI_GRAPHLAYOUT_H