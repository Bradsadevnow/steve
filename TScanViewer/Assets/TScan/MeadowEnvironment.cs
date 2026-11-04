using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Steve.TScan {
 // Scene-owned environment. Its definition and visuals exist without an agent or server.
 [ExecuteAlways,DefaultExecutionOrder(-100)]
 public sealed class MeadowEnvironment:MonoBehaviour {
  [Serializable] class Part {public string name,key;public float[] vertices,normals,colors;public int[] triangles;}
  [Serializable] class Instance {public string prototype;public Vector3 position,scale;public float yaw;}
  [Serializable] class Art {public Part[] prototypes;public Instance[] instances;}
  public MeadowWorldDefinition definition;
  public GridFlagVisuals Flags {get;private set;}
  GameObject generated;
  Material material;
  readonly List<Mesh> meshes=new List<Mesh>();
  string renderedManifest;
  public static Vector3 Cell(int col,int row)=>new Vector3(2*col-11,0,2*row-11);
  void OnEnable(){Rebuild();}
  void Update(){if(definition && renderedManifest!=definition.ManifestJson)Rebuild();}
  static void Release(UnityEngine.Object value){if(!value)return;if(Application.isPlaying)Destroy(value);else DestroyImmediate(value);}
  Mesh MakeMesh(Part part){
   var mesh=new Mesh{name=part.name,indexFormat=IndexFormat.UInt32,hideFlags=HideFlags.DontSave};
   int count=part.vertices.Length/3;var vertices=new Vector3[count];var normals=new Vector3[count];var colors=new Color[count];
   for(int i=0;i<count;i++){vertices[i]=new Vector3(part.vertices[3*i],part.vertices[3*i+1],part.vertices[3*i+2]);normals[i]=new Vector3(part.normals[3*i],part.normals[3*i+1],part.normals[3*i+2]);colors[i]=new Color(part.colors[4*i],part.colors[4*i+1],part.colors[4*i+2],part.colors[4*i+3]);}
   mesh.vertices=vertices;mesh.normals=normals;mesh.colors=colors;mesh.triangles=part.triangles;mesh.RecalculateBounds();meshes.Add(mesh);return mesh;
  }
  public void Rebuild(){
   Clear();if(!definition)return;
   renderedManifest=definition.ManifestJson;
   generated=new GameObject("Meadow visuals (from world definition)"){hideFlags=HideFlags.DontSave};generated.transform.SetParent(transform,false);
   material=new Material(Shader.Find("Steve/MeadowVertex")){hideFlags=HideFlags.DontSave};
   var art=JsonUtility.FromJson<Art>(Resources.Load<TextAsset>("Meadow/field").text);var prototypes=new Dictionary<string,Mesh>();
   foreach(var part in art.prototypes)prototypes[part.key]=MakeMesh(part);
   var combine=new CombineInstance[art.instances.Length];
   for(int i=0;i<combine.Length;i++){var item=art.instances[i];combine[i]=new CombineInstance{mesh=prototypes[item.prototype],transform=Matrix4x4.TRS(item.position,Quaternion.Euler(0,item.yaw,0),item.scale)};}
   var field=new Mesh{name="Meadow / combined visual field",indexFormat=IndexFormat.UInt32,hideFlags=HideFlags.DontSave};field.CombineMeshes(combine);meshes.Add(field);
   var ground=new GameObject("Flat meadow / decoration has no collision"){layer=30,hideFlags=HideFlags.DontSave};ground.transform.SetParent(generated.transform,false);ground.AddComponent<MeshFilter>().sharedMesh=field;ground.AddComponent<MeshRenderer>().sharedMaterial=material;
   Flags=generated.AddComponent<GridFlagVisuals>();Flags.Refresh(definition.manifest.landmarks);
   if(Application.isPlaying)generated.AddComponent<GridCompassVisuals>();
   var sunlight=new GameObject("Meadow daylight"){hideFlags=HideFlags.DontSave};sunlight.transform.SetParent(generated.transform,false);sunlight.transform.localRotation=Quaternion.Euler(48,-35,0);
   var sun=sunlight.AddComponent<Light>();sun.type=LightType.Directional;sun.color=new Color(1,.93f,.8f);sun.intensity=1;sun.cullingMask=1<<30;
  }
  void Clear(){if(generated){generated.SetActive(false);Release(generated);}generated=null;Flags=null;foreach(var mesh in meshes)Release(mesh);meshes.Clear();Release(material);material=null;}
  void OnDisable(){Clear();}
 }
}
