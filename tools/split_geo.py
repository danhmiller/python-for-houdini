def split_geo():    
    import hou
    # Set colors for nodes
    muted_olive_green = hou.Color((0.302, 0.522, 0.114))
    solid_vivid_blue = hou.Color((0.090, 0.369, 0.686))
    vibrant_amber_yellow = hou.Color((1.0, 0.722, 0.0))
    black_color = hou.Color((0.0, 0.0, 0.0))

    # Get the selected node
    selected_node = hou.selectedNodes()
    # Check if the node is selected
    if not selected_node:
        hou.ui.displayMessage('No node is selected')
        raise ValueError ('No node is selected')
        
    # Set working context  
    selected_node = selected_node[0]
    parent_node = selected_node.parent()
    geo_info = selected_node.geometry()

    # Ask user for the attribute name in order to split geo
    pressed_button, attrib_name = hou.ui.readInput(
        "Provide the attribute's name to split the geometry: ", 
        buttons=('OK', 'Cancle')
    )
    if pressed_button == 1 or not attrib_name:
        hou.ui.displayMessage("No attribute provided. Try again.")
        raise ValueError ("No attribute provided. Try again.")

    # Check if it is point or primitive attrib
    split_attrib = geo_info.findPrimAttrib(attrib_name)
    attrib_class = "prims"
    if not split_attrib:
        split_attrib = geo_info.findPointAttrib(attrib_name)
        attrib_class = "points"
        if not split_attrib:
            hou.ui.displayMessage(f"The specified attribute - {attrib_name} - does not exit.")
            raise ValueError(f"The specified attribute - {attrib_name} - does not exit.")

    # Check if the attribute is valid    
    # Get values
    unique_val = set()
    if attrib_class == "prims":
        for prim in geo_info.prims():
            unique_val.add(prim.attribValue(attrib_name))
    elif attrib_class == "points":
        for pt in geo_info.points():
            unique_val.add(pt.attribValue(attrib_name))
    # Creating nodes
    # Merge node
    merge_node = parent_node.createNode('merge')
    merge_node.setColor(black_color)
    selected_node.setColor(muted_olive_green)
    nodes_to_layout = [selected_node, merge_node]

    # Create Blast node:group, negated
    for index, value in enumerate(unique_val):
        blast_node = parent_node.createNode('blast')
        blast_node.parm('group').set(f"@{attrib_name}={value}")
        parm = blast_node.parm("grouptype")
        print(parm.menuItems())
        blast_node.parm('grouptype').set(attrib_class) # attrib_class matched grouptype
        blast_node.parm('negate').set(1)
        
        blast_node.setInput(0, selected_node)
        blast_node.setColor(solid_vivid_blue)
    # Null node
        null_node = parent_node.createNode('null', f"{value}")
        null_node.setInput(0, blast_node)
        null_node.setColor(vibrant_amber_yellow)
        
        merge_node.setInput(index, null_node)
        nodes_to_layout.extend([blast_node, null_node])
    # Layout nodes
    parent_node.layoutChildren(items = nodes_to_layout)

    # Set display/render flags on Merge node
    merge_node.setDisplayFlag(1)
    merge_node.setRenderFlag(1)

