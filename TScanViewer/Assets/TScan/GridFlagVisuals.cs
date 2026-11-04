using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Steve.TScan {
 // Presentation of the Unity-authored world definition, independent of agent state.
 [ExecuteAlways]
 public sealed class GridFlagVisuals:MonoBehaviour {
  sealed class Cloth {public Mesh mesh;public Vector3[] rest,work;public float phase;}
  readonly List<GameObject> roots=new List<GameObject>();readonly List<Material> materials=new List<Material>();readonly List<Cloth> cloths=new List<Cloth>();
  string signature="";public int FlagCount=>roots.Count;
  static Color FlagColor(string color)=>color=="blue"?new Color(.08f,.4f,.98f):color=="red"?new Color(.92f,.1f,.16f):color=="yellow"?new Color(1,.83f,.08f):color=="purple"?new Color(.62f,.2f,.9f):new Color(1,.39f,.055f);
  static void Release(UnityEngine.Object value){if(!value)return;if(Application.isPlaying)Destroy(value);else DestroyImmediate(value);}
  Material Surface(Color color){var m=new Material(Shader.Find("Universal Render Pipeline/Lit")){hideFlags=HideFlags.DontSave};m.SetColor("_BaseColor",color);m.SetFloat("_Smoothness",.22f);m.SetFloat("_Cull",0);materials.Add(m);return m;}
  GameObject Primitive(string name,PrimitiveType type,Transform parent,Vector3 position,Vector3 scale,Material material){var o=GameObject.CreatePrimitive(type);o.hideFlags=HideFlags.DontSave;o.name=name;o.layer=30;o.transform.SetParent(parent,false);o.transform.localPosition=position;o.transform.localScale=scale;var collider=o.GetComponent<Collider>();if(collider){collider.enabled=false;Release(collider);}o.GetComponent<Renderer>().sharedMaterial=material;return o;}
  public void Refresh(GridLandmark[] landmarks){
   if(landmarks==null)return;var next=string.Join(";",landmarks.Select(t=>$"{t.id}:{t.col}:{t.row}:{t.color}"));if(next==signature)return;signature=next;Clear();
   var pole=Surface(new Color(.78f,.72f,.54f));
   for(int f=0;f<landmarks.Length;f++){
    var data=landmarks[f];var root=new GameObject("Flag / "+data.name){hideFlags=HideFlags.DontSave};root.layer=30;root.transform.SetParent(transform,false);root.transform.localPosition=MeadowEnvironment.Cell(data.col,data.row);roots.Add(root);var color=Surface(FlagColor(data.color));
    Primitive("Occupiable colored landing marker",PrimitiveType.Cylinder,root.transform,new Vector3(0,.019f,0),new Vector3(.7f,.018f,.7f),color);
    var offset=new Vector3(.64f,0,.64f);Primitive("Flagpole",PrimitiveType.Cylinder,root.transform,offset+Vector3.up*.9f,new Vector3(.045f,.9f,.045f),pole);Primitive("Finial",PrimitiveType.Sphere,root.transform,offset+Vector3.up*1.82f,Vector3.one*.1f,pole);
    Primitive("Pole foot",PrimitiveType.Cylinder,root.transform,offset+Vector3.up*.04f,new Vector3(.19f,.04f,.19f),pole);
    const int steps=12;var v=new Vector3[(steps+1)*2];var triangles=new int[steps*6];
    for(int i=0;i<=steps;i++){float x=i/(float)steps*.88f;float sag=.065f*Mathf.Sin(i/(float)steps*Mathf.PI);v[i*2]=offset+new Vector3(x,1.12f-sag,0);v[i*2+1]=offset+new Vector3(x,1.68f-sag,0);if(i<steps){int j=i*2,k=i*6;triangles[k]=j;triangles[k+1]=j+1;triangles[k+2]=j+3;triangles[k+3]=j;triangles[k+4]=j+3;triangles[k+5]=j+2;}}
    var mesh=new Mesh{name=data.name+" / cosmetic fabric",hideFlags=HideFlags.DontSave};mesh.vertices=v;mesh.triangles=triangles;mesh.RecalculateNormals();mesh.RecalculateBounds();var fabric=new GameObject("Colored fabric / "+data.id){hideFlags=HideFlags.DontSave};fabric.layer=30;fabric.transform.SetParent(root.transform,false);fabric.AddComponent<MeshFilter>().sharedMesh=mesh;fabric.AddComponent<MeshRenderer>().sharedMaterial=color;cloths.Add(new Cloth{mesh=mesh,rest=v,work=(Vector3[])v.Clone(),phase=f*1.7f});

   }
  }
  void LateUpdate(){
   foreach(var c in cloths){for(int i=0;i<c.work.Length;i++){var p=c.rest[i];float t=(p.x-.64f)/.88f;p.z+=Mathf.Sin(Time.unscaledTime*2.4f-t*5+c.phase)*.09f*t;c.work[i]=p;}c.mesh.vertices=c.work;c.mesh.RecalculateNormals();}
  }
  void Clear(){foreach(var o in roots)if(o)Release(o);foreach(var c in cloths)if(c.mesh)Release(c.mesh);foreach(var m in materials)if(m)Release(m);roots.Clear();cloths.Clear();materials.Clear();}
  void OnDestroy(){Clear();}
 }
}
