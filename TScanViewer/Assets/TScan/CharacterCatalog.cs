using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace Steve.TScan {
 [Serializable] public class CharacterSocket {public string id,type;public float x,y,z,qx,qy,qz,qw=1;public Vector3 Position=>new Vector3(x,y,z);public Quaternion Rotation=>new Quaternion(qx,qy,qz,qw).normalized;}
 [Serializable] public class CharacterPair {public string primary,secondary;}
 [Serializable] public class CharacterBody {public string id,name,mesh;public CharacterSocket[] sockets;public CharacterPair[] pairs;}
 [Serializable] public class CharacterStatModifier {public string stat;public int amount;}
 [Serializable] public class CharacterModule {public string id,name,mesh,description;public string[] mount_types,actions;public int slots;public CharacterStatModifier[] stat_modifiers;public CharacterAbilityView[] abilities;}
 [Serializable] public class CharacterEquipment {public string socket_id,module_id;}
 [Serializable] public class CharacterState {public string character_id="steve",catalog_version,body_id="hover";public int revision;public CharacterEquipment[] equipment=Array.Empty<CharacterEquipment>();public string[] capabilities=Array.Empty<string>();public CharacterSheetSnapshot sheet;}
 [Serializable] public class CharacterCatalogData {public string version;public CharacterBody[] bodies;public CharacterModule[] modules;}
 [Serializable] public class CharacterApplyRequest {public string request_id,character_id="steve",catalog_version,body_id;public int expected_revision;public CharacterEquipment[] equipment;}
 [Serializable] public class CharacterApplyReceipt {public string outcome,error,request_id,catalog_hash;public CharacterState character;}
 [Serializable] public class CharacterPreviewRequest {public string character_id="steve",catalog_version,body_id;public int expected_revision;public CharacterEquipment[] equipment;}
 [Serializable] public class CharacterPreviewReceipt {public bool preview;public int expected_revision;public CharacterState character;public string error;}
 [Serializable] public class TrainingTarget {public string id,prototype;public int col,row,hp,max_hp;}
 public static class CharacterCatalog {
  static CharacterCatalogData data;static readonly Dictionary<string,Mesh> meshes=new Dictionary<string,Mesh>();static Material material;
  public static CharacterCatalogData Data=>data??(data=JsonUtility.FromJson<CharacterCatalogData>(Resources.Load<TextAsset>("Meadow/character/catalog").text));
  public static CharacterBody Body(string id)=>Data.bodies.FirstOrDefault(b=>b.id==id);
  public static CharacterModule Module(string id)=>Data.modules.FirstOrDefault(m=>m.id==id);
  public static string Validate(CharacterState state){
   if(state==null||state.equipment==null)return "Invalid character preset: missing equipment list.";
   if(state.catalog_version!=Data.version)return "Catalog version mismatch. Reload the current equipment catalog.";
   var body=Body(state.body_id);if(body==null)return "Unknown body: "+state.body_id;
   var occupied=new HashSet<string>();
   foreach(var item in state.equipment??Array.Empty<CharacterEquipment>()){
    if(item==null||string.IsNullOrEmpty(item.socket_id)||string.IsNullOrEmpty(item.module_id))return "Each module assignment needs a socket and module ID.";
    var slot=body.sockets.FirstOrDefault(s=>s.id==item.socket_id);var module=Module(item.module_id);
    if(slot==null)return "Remap or remove "+item.module_id+": this body has no "+item.socket_id+" mount.";
    if(module==null)return "Unknown module: "+item.module_id;
    if(!module.mount_types.Contains(slot.type))return module.name+" does not fit "+slot.id+" ("+slot.type+").";
    var sites=new List<string>{slot.id};
    if(module.slots==2){var pair=body.pairs.FirstOrDefault(p=>p.primary==slot.id);if(pair==null)return module.name+" requires a two-mount primary socket.";sites.Add(pair.secondary);}
    foreach(var site in sites)if(!occupied.Add(site))return "Mount conflict at "+site+". Unequip the conflicting module first.";
   }
   return null;
  }
  public static CharacterState Copy(CharacterState state)=>JsonUtility.FromJson<CharacterState>(JsonUtility.ToJson(state));
  public static string VisualKey(CharacterState state)=>state==null?"":state.body_id+"|"+string.Join("|",(state.equipment??Array.Empty<CharacterEquipment>()).Select(e=>e.socket_id+":"+e.module_id));
  public static Mesh Mesh(string id){
   if(meshes.TryGetValue(id,out var found)&&found)return found;
   // A missing lookup must not destroy meshes already used by live characters.
   if(meshes.Count>0)return null;
   using(var r=new BinaryReader(new MemoryStream(Resources.Load<TextAsset>("Meadow/character/meshes").bytes))){
    if(System.Text.Encoding.ASCII.GetString(r.ReadBytes(4))!="SKIT")throw new InvalidDataException("Invalid character mesh format");r.ReadUInt32();uint count=r.ReadUInt32();
    for(int i=0;i<count;i++){
     var key=System.Text.Encoding.UTF8.GetString(r.ReadBytes(r.ReadUInt16()));int nv=(int)r.ReadUInt32(),ni=(int)r.ReadUInt32();var vertices=new Vector3[nv];var normals=new Vector3[nv];var colors=new Color32[nv];var indices=new int[ni];
     for(int j=0;j<nv;j++)vertices[j]=new Vector3(r.ReadSingle(),r.ReadSingle(),r.ReadSingle());
     for(int j=0;j<nv;j++){normals[j]=new Vector3(r.ReadSByte(),r.ReadSByte(),r.ReadSByte()).normalized;r.ReadByte();}
     for(int j=0;j<nv;j++)colors[j]=new Color32(r.ReadByte(),r.ReadByte(),r.ReadByte(),r.ReadByte());
     for(int j=0;j<ni;j++)indices[j]=r.ReadInt32();
     var mesh=new Mesh{name=key,indexFormat=IndexFormat.UInt32,hideFlags=HideFlags.DontSave};mesh.vertices=vertices;mesh.normals=normals;mesh.colors32=colors;mesh.triangles=indices;mesh.RecalculateBounds();meshes[key]=mesh;
    }
   }
   return meshes.TryGetValue(id,out found)?found:null;
  }
  static GameObject Piece(string id,Transform parent,int layer,Vector3 position){
   var mesh=Mesh(id);if(!mesh)return null;
   if(!material)material=new Material(Shader.Find("Steve/MeadowVertex")){hideFlags=HideFlags.DontSave};
   var go=new GameObject(id){layer=layer,hideFlags=HideFlags.DontSave};go.transform.SetParent(parent,false);go.transform.localPosition=position;
   go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=material;
   return go;
  }
  public static GameObject Create(CharacterState state,Transform parent,int layer,bool showMounts=false){
   var body=Body(state.body_id);var root=new GameObject("Character / "+state.body_id){layer=layer,hideFlags=HideFlags.DontSave};root.transform.SetParent(parent,false);
   if(body==null)return root;
   if(!string.IsNullOrEmpty(body.mesh))Piece(body.mesh,root.transform,layer,Vector3.zero);
   foreach(var item in state.equipment??Array.Empty<CharacterEquipment>()){
    var slot=body.sockets.FirstOrDefault(s=>s.id==item.socket_id);var mod=Module(item.module_id);
    if(slot!=null&&mod!=null&&mod.mount_types.Contains(slot.type)){var piece=Piece(mod.mesh,root.transform,layer,slot.Position);if(piece)piece.transform.localRotation=slot.Rotation;}
   }
   if(showMounts)foreach(var slot in body.sockets){var marker=GameObject.CreatePrimitive(PrimitiveType.Sphere);marker.name="Mount / "+slot.id;marker.layer=layer;UnityEngine.Object.Destroy(marker.GetComponent<Collider>());marker.transform.SetParent(root.transform,false);marker.transform.localPosition=slot.Position;marker.transform.localScale=Vector3.one*.10f;marker.GetComponent<Renderer>().sharedMaterial=material;}
   return root;
  }
 }
}
