using System;
using System.Linq;
using UnityEngine;

namespace Steve.TScan {
 // Optional read-only sheet projection. No UI code initializes or evaluates gameplay stats.
 [Serializable] public class CharacterResourceView {public float current,maximum;}
 [Serializable] public class CharacterAttributeView {public string id;public float base_value,level_bonus,equipment_bonus,temporary_bonus,effective;}
 [Serializable] public class CharacterAbilityView {public string id,name,stat,description,rules_version;public int damage,effective_stat,reach,numerator,denominator,minimum,stats_revision;}
 [Serializable] public class CharacterSheetSnapshot {public string schema,rules_version,resource_rules_version;public int revision,level;public CharacterResourceView hp,mp;public CharacterAttributeView[] attributes;public CharacterAbilityView[] abilities;}

 public sealed class CharacterPresentation {
  public static readonly string[] Attributes={"STR","DEX","INT","WIS","CON"};
  public CharacterState Character {get;private set;}
  public CharacterSheetSnapshot Sheet=>Character?.sheet?.revision>0?Character.sheet:null;
  public bool Fresh {get;private set;}
  public string Status {get;private set;}="Waiting";
  public string Position {get;private set;}="Position unavailable";
  public string Observation {get;private set;}="";
  public void Update(GridSnapshot snapshot,bool ready,string status){
   Fresh=ready&&snapshot?.character!=null;Status=status;
   if(!Fresh)return;
   Character=snapshot.character;Observation=snapshot.observation_id;
   Position=snapshot.self==null?"Position unavailable":"x "+snapshot.self.col+" · y "+snapshot.self.row;
  }
  public CharacterAttributeView Attribute(string id)=>Sheet?.attributes?.FirstOrDefault(a=>a!=null&&string.Equals(a.id,id,StringComparison.OrdinalIgnoreCase));
  public static bool Finite(float value)=>!float.IsNaN(value)&&!float.IsInfinity(value);
  public static bool Valid(CharacterResourceView value)=>value!=null&&Finite(value.current)&&Finite(value.maximum)&&value.maximum>0&&value.current>=0&&value.current<=value.maximum;
  public static string Number(float value)=>Finite(value)?value.ToString("0.##",System.Globalization.CultureInfo.InvariantCulture):"—";
  public static string Name(string id)=>string.IsNullOrEmpty(id)?"—":id.Replace('_',' ');
  public static string ModuleName(string id)=>CharacterCatalog.Module(id)?.name??Name(id);
  public static Texture2D ModuleIcon(string id){
   return string.IsNullOrEmpty(id)?null:Resources.Load<Texture2D>("Meadow/character/thumbnails/"+id);
  }
  public static string AbilityDetails(CharacterAbilityView ability)=>ability.name+" · "+ability.damage+" damage\n"+ability.stat+" "+ability.effective_stat+" · "+ability.description;
  public static string DraftComparison(CharacterState confirmed,CharacterState draft,CharacterState preview=null){
   if(confirmed==null||draft==null)return "Waiting for confirmed equipment.";
   var validation=CharacterCatalog.Validate(draft);
   var before=confirmed.equipment??Array.Empty<CharacterEquipment>();var after=draft.equipment??Array.Empty<CharacterEquipment>();
   Func<CharacterEquipment,string> key=e=>e.socket_id+":"+e.module_id;
   var removed=before.Where(e=>!after.Any(a=>key(a)==key(e))).Select(e=>"− "+Name(e.socket_id)+": "+ModuleName(e.module_id));
   var added=after.Where(e=>!before.Any(b=>key(b)==key(e))).Select(e=>"+ "+Name(e.socket_id)+": "+ModuleName(e.module_id));
   var changes=removed.Concat(added).ToList();
   if(confirmed.body_id!=draft.body_id)changes.Insert(0,"Body: "+(CharacterCatalog.Body(confirmed.body_id)?.name??confirmed.body_id)+" → "+(CharacterCatalog.Body(draft.body_id)?.name??draft.body_id));
   if(validation!=null)changes.Add("Resolve before Apply: "+validation);
   else{
    var grants=after.Select(e=>CharacterCatalog.Module(e.module_id)).Where(m=>m!=null).SelectMany(m=>m.actions??Array.Empty<string>()).Distinct().ToArray();
    var current=confirmed.capabilities??Array.Empty<string>();
    foreach(var action in grants.Except(current))changes.Add("Gains "+Name(action));
    foreach(var action in current.Except(grants))changes.Add("Loses "+Name(action));
   }
   if(changes.Count==0)changes.Add("Equipment matches the confirmed loadout.");
   if(validation==null&&preview?.sheet?.revision>0){
    foreach(var stat in preview.sheet.attributes??Array.Empty<CharacterAttributeView>()){
     var current=confirmed.sheet?.attributes?.FirstOrDefault(a=>a.id==stat.id);
     changes.Add(stat.id+": "+(current==null?"—":Number(current.effective))+" → "+Number(stat.effective));
    }
    foreach(var ability in preview.sheet.abilities??Array.Empty<CharacterAbilityView>())changes.Add(ability.name+": "+ability.damage+" damage ("+ability.stat+" "+ability.effective_stat+")");
    changes.Add("Engine preview · not applied");
   }else changes.Add("Waiting for an engine stat preview.");
   return string.Join("\n",changes);
  }
 }
}
