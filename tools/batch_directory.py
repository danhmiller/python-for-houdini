## Ask the user for the files
# Geometry node
# File node for FBX, OBJ and BGEO file
# If it is ABC file we use Alembic loader
# Transform to Houdini scale 0.01
# Add Material
# Merge
def batch_directory():
    import hou
    defaut_directory = hou.text.expandString('$HIP')

    select_directory = hou.ui.selectFile(start_directory = defaut_directory,
                                        title = 'Select the files you want to import',
                                        file_type = hou.fileType.Geometry,
                                        multiple_select = True)
    if select_directory:
        select_directory = select_directory.split(';')
        obj = hou.node('/obj')
        geo_node = obj.createNode('geo', node_name = 'chess')
        merge_node = geo_node.createNode('merge')
        merge_input = 0
    # Ask the user for the uniform scale to convert the files to Houdini scale   
        pressed_button, scale_val = hou.ui.readInput(
        'Enter the uniform scale value:', 
        buttons = ('OK', 'Cancel')
        )
        if pressed_button == 1 or not scale_val:
            hou.ui.displayMessage('No scale value valid')
            raise ValueError('Invalid scale value provided.')
        scale_val = float(scale_val)
            
        for item in select_directory:
            item = item.strip()
            asset = item.split('/')
            object = asset[-1].split('.') #object[0] is the name, object[-1] is the extension
            if object[-1] == 'abc':
                abc_file_loader = geo_node.createNode('alembic', node_name = object[0])
                abc_file_loader.parm('fileName').set(item)
                unpack_node = geo_node.createNode('unpack')
                unpack_node.setInput(0, abc_file_loader)
                transform_input = unpack_node           
            else:
                new_file_loader = geo_node.createNode('file', node_name = object[0])
                new_file_loader.parm('file').set(item)
                transform_input = new_file_loader
            transform_node = geo_node.createNode('xform')
            transform_node.setInput(0, transform_input)
            transform_node.parm('scale').set(scale_val)
            
            material_node = geo_node.createNode('material')
            material_node.setInput(0, transform_node)
            merge_node.setInput(merge_input, material_node)
            merge_input +=1
        geo_node.layoutChildren()
    else:
        hou.ui.displayMessage('No valid file selected. Please try again.', buttons=('OK',))


    
    
    
    