using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Steve.TScan {
 // Scene-owned environment. Its definition and visuals exist without an agent or server.
 [ExecuteAlways,DefaultExecutionOrder(-100)]
 public sealed class MeadowEnvironment:MonoBehaviour {
  public const string KitSchema="meadow-world-v3";
  [Serializable] class Part {public string name,key;public float[] vertices,normals,colors;public int[] triangles;}
  [Serializable] class Instance {public string prototype;public Vector3 position,scale;public float yaw;}
  [Serializable] class Art {public Part[] prototypes;public Instance[] instances;}
  public MeadowWorldDefinition definition;
  // A draft being edited by the world builder. While set, it is drawn instead of the published definition.
  public MeadowManifest Override {get;set;}
  public GridFlagVisuals Flags {get;private set;}
  public Transform Root=>generated?generated.transform:transform;
  GameObject generated;
  Material material;
  readonly List<Mesh> meshes=new List<Mesh>();
  string renderedManifest;
  public static Vector3 Cell(int col,int row)=>new Vector3(2*col-16,0,2*row-16);
  public MeadowManifest Active=>Override??definition?.manifest;
  void OnEnable(){Rebuild();}
  void Update(){if(definition && Override==null && renderedManifest!=definition.ManifestJson)Rebuild();}
  static void Release(UnityEngine.Object value){if(!value)return;if(Application.isPlaying)Destroy(value);else DestroyImmediate(value);}
  Mesh MakeMesh(Part part){
   var mesh=new Mesh{name=part.name,indexFormat=IndexFormat.UInt32,hideFlags=HideFlags.DontSave};
   int count=part.vertices.Length/3;var vertices=new Vector3[count];var normals=new Vector3[count];var colors=new Color[count];
   for(int i=0;i<count;i++){vertices[i]=new Vector3(part.vertices[3*i],part.vertices[3*i+1],part.vertices[3*i+2]);normals[i]=new Vector3(part.normals[3*i],part.normals[3*i+1],part.normals[3*i+2]);colors[i]=new Color(part.colors[4*i],part.colors[4*i+1],part.colors[4*i+2],part.colors[4*i+3]);}
   mesh.vertices=vertices;mesh.normals=normals;mesh.colors=colors;mesh.triangles=part.triangles;mesh.RecalculateBounds();meshes.Add(mesh);return mesh;
  }
  public void Rebuild(){
   Clear();if(!definition)return;
   var manifest=Active;
   renderedManifest=Override==null?definition.ManifestJson:null;
   generated=new GameObject("Meadow visuals (from world definition)"){hideFlags=HideFlags.DontSave};generated.transform.SetParent(transform,false);
   material=new Material(Shader.Find("Steve/MeadowVertex")){hideFlags=HideFlags.DontSave};
   if(manifest.schema==KitSchema)BuildKit(manifest);else BuildMeadow(manifest);
   Flags=generated.AddComponent<GridFlagVisuals>();Flags.Refresh(manifest.landmarks);
   if(Application.isPlaying)generated.AddComponent<GridCompassVisuals>();
   var sunlight=new GameObject("Meadow daylight"){hideFlags=HideFlags.DontSave};sunlight.transform.SetParent(generated.transform,false);sunlight.transform.localRotation=Quaternion.Euler(48,-35,0);
   var sun=sunlight.AddComponent<Light>();sun.type=LightType.Directional;sun.color=new Color(1,.93f,.8f);sun.intensity=1;sun.cullingMask=1<<30;
  }
  // v3: one instance per placed kit piece. Meshes are shared, so rebuilding while editing is cheap.
  void BuildKit(MeadowManifest manifest){
   WorldKit.EnsureLoaded();
   var floors=new GameObject("Floors"){hideFlags=HideFlags.DontSave};floors.transform.SetParent(generated.transform,false);
   var objects=new GameObject("Placed pieces"){hideFlags=HideFlags.DontSave};objects.transform.SetParent(generated.transform,false);
   for(int i=0;i<manifest.floors.Length;i++)Spawn(floors.transform,manifest.floors[i],i%manifest.columns+1,i/manifest.columns+1,0,"Floor "+(i%manifest.columns+1)+","+(i/manifest.columns+1));
   foreach(var item in manifest.obstacles)Spawn(objects.transform,item.prototype,item.col,item.row,item.yaw,item.id);
   foreach(var item in manifest.props)Spawn(objects.transform,item.prototype,item.col,item.row,item.yaw,item.id);
  }
  public GameObject Spawn(Transform parent,string prototype,int col,int row,int yaw,string label){
   var mesh=WorldKit.MeshOf(prototype);if(!mesh)return null;
   var piece=new GameObject(label){layer=30,hideFlags=HideFlags.DontSave};piece.transform.SetParent(parent,false);
   piece.transform.localPosition=Cell(col,row);piece.transform.localRotation=Quaternion.Euler(0,yaw,0);
   piece.AddComponent<MeshFilter>().sharedMesh=mesh;piece.AddComponent<MeshRenderer>().sharedMaterial=material;return piece;
  }
  public Material PieceMaterial=>material;
  // v1/v2: the baked meadow ground plus a few baked obstacle prototypes.
  void BuildMeadow(MeadowManifest manifest){
   var art=JsonUtility.FromJson<Art>(Resources.Load<TextAsset>("Meadow/course").text);var prototypes=new Dictionary<string,Mesh>();
   foreach(var part in art.prototypes)prototypes[part.key]=MakeMesh(part);
   var obstacles=manifest.obstacles;
   var combine=new CombineInstance[1+obstacles.Length];
   combine[0]=new CombineInstance{mesh=prototypes["ground"],transform=Matrix4x4.identity};
   for(int i=0;i<obstacles.Length;i++){var item=obstacles[i];combine[i+1]=new CombineInstance{mesh=prototypes[item.prototype],transform=Matrix4x4.TRS(Cell(item.col,item.row),Quaternion.identity,Vector3.one)};}
   var field=new Mesh{name="Meadow / combined visual field",indexFormat=IndexFormat.UInt32,hideFlags=HideFlags.DontSave};field.CombineMeshes(combine);meshes.Add(field);
   var ground=new GameObject("Flat meadow / decoration has no collision"){layer=30,hideFlags=HideFlags.DontSave};ground.transform.SetParent(generated.transform,false);ground.AddComponent<MeshFilter>().sharedMesh=field;ground.AddComponent<MeshRenderer>().sharedMaterial=material;
  }
  void Clear(){if(generated){generated.SetActive(false);Release(generated);}generated=null;Flags=null;foreach(var mesh in meshes)Release(mesh);meshes.Clear();Release(material);material=null;}
  void OnDisable(){Clear();}
 }
}
