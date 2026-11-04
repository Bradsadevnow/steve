"""Explicit synthetic environment publisher for backend tests, never production setup."""
def manifest():
 return dict(schema='meadow-world-v1',world_id='steve_grid_v1',revision=1,columns=10,rows=10,landmarks=[dict(id='target_'+color,name=color.capitalize()+' flag',kind='flag',color=color,col=col,row=row,occupiable=True) for color,col,row in [('blue',8,7),('red',2,8),('yellow',9,2),('purple',2,2),('orange',6,10)]])
def publish(world,client='test'):
 return world.register_world(client,manifest())
def poll(world,client='test'):
 return world.poll(client,world.observe()['world_manifest_hash'])
