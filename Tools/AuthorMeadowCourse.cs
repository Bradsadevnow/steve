// Run in the Unity Editor through script eval_file. Unity owns this layout.
var world = UnityEditor.AssetDatabase.LoadAssetAtPath<Steve.TScan.MeadowWorldDefinition>("Assets/Resources/Meadow/World.asset");
UnityEditor.Undo.RecordObject(world,"Install approved 15x15 meadow course");
var m = world.manifest;
m.schema="meadow-world-v2";m.revision=System.Math.Max(2,m.revision+1);m.columns=15;m.rows=15;
m.spawn=new Steve.TScan.MeadowCell{col=8,row=8};
m.landmarks=new[]{
 new Steve.TScan.GridLandmark{id="target_blue",name="Blue flag",kind="flag",color="blue",col=1,row=15,occupiable=true},
 new Steve.TScan.GridLandmark{id="target_red",name="Red flag",kind="flag",color="red",col=15,row=15,occupiable=true},
 new Steve.TScan.GridLandmark{id="target_yellow",name="Yellow flag",kind="flag",color="yellow",col=15,row=1,occupiable=true},
 new Steve.TScan.GridLandmark{id="target_purple",name="Purple flag",kind="flag",color="purple",col=1,row=1,occupiable=true}};
var blocks=new System.Collections.Generic.List<Steve.TScan.MeadowObstacle>();
System.Action<string,int,int> add=(prototype,x,y)=>blocks.Add(new Steve.TScan.MeadowObstacle{id=prototype+"_"+x+"_"+y,prototype=prototype,col=x,row=y});
for(int x=3;x<=9;x++)add("stone_wall",x,5);
for(int x=7;x<=13;x++)add("hedge",x,11);
foreach(var c in new[]{new[]{4,8},new[]{5,8},new[]{11,8},new[]{12,8},new[]{7,13},new[]{9,3}})add("boulder_cluster",c[0],c[1]);
foreach(var c in new[]{new[]{3,3},new[]{13,13},new[]{3,12},new[]{12,3}})add("wood_hurdle",c[0],c[1]);
m.obstacles=blocks.ToArray();
UnityEditor.EditorUtility.SetDirty(world);UnityEditor.AssetDatabase.SaveAssets();
var environment=UnityEngine.Object.FindFirstObjectByType<Steve.TScan.MeadowEnvironment>();environment.Rebuild();
return world.ManifestJson;
