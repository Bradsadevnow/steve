import bpy,json
print('CHASSIS_INSPECT '+json.dumps([{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'dimensions':list(o.dimensions),'hidden':o.hide_render,'props':{k:str(v) for k,v in o.items()}} for o in bpy.data.objects if o.type in {'EMPTY','CAMERA'} or o.parent is None]))
print('COLLECTIONS '+json.dumps([{'name':c.name,'count':len(c.all_objects),'hidden':c.hide_render} for c in bpy.data.collections]))
