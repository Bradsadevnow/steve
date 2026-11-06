#if UNITY_EDITOR
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Steve.TScan;

namespace Steve.TScan.EditorTools {
 // One-off: move the shipped World.asset from the baked meadow (v2) to the classified kit (v3), keeping its authored
 // flags, spawn and obstacle cells. Baked meadow prototypes are replaced by the nearest kit piece.
 public static class WorldMigration {
  static readonly Dictionary<string,string> Replacement=new Dictionary<string,string>{
   {"stone_wall","dungeon_wall_plain"},{"wood_hurdle","dungeon_prop_crate"},{"boulder_cluster","dungeon_prop_rubble"},{"hedge","dungeon_prop_crate_stack"}};
  static readonly string[] FloorMix={"dungeon_floor_flag_a","dungeon_floor_flag_a","dungeon_floor_flag_b","dungeon_floor_flag_c","dungeon_floor_flag_a","dungeon_floor_mossy"};

  [MenuItem("Steve/Migrate world definition to kit v3")]
  public static void Migrate(){
   const string path="Assets/Resources/Meadow/World.asset";
   var definition=AssetDatabase.LoadAssetAtPath<MeadowWorldDefinition>(path);
   if(definition==null){Debug.LogError("World.asset not found");return;}
   WorldKit.Reload();
   var source=definition.manifest;
   if(source.schema==MeadowEnvironment.KitSchema){Debug.Log("World.asset is already a kit world (revision "+source.revision+").");return;}
   foreach(var o in source.obstacles)if(Replacement.TryGetValue(o.prototype,out var piece))o.prototype=piece;
   var builder=new WorldBuilder(source);
   for(int row=1;row<=WorldBuilder.Size;row++)for(int col=1;col<=WorldBuilder.Size;col++){
    var pick=FloorMix[(col*7+row*13+col*row)%FloorMix.Length];
    builder.TryPlace(WorldKit.Info(pick),col,row,0,true,out _);
   }
   var lost=builder.Unreachable();if(lost!=null)Debug.LogWarning("Migrated world: "+lost);
   definition.manifest=builder.ToManifest(source.revision+1);
   EditorUtility.SetDirty(definition);AssetDatabase.SaveAssets();
   Debug.Log("Migrated World.asset to "+definition.manifest.schema+" revision "+definition.manifest.revision+": "+definition.manifest.obstacles.Length+" obstacles, "+definition.manifest.props.Length+" props, "+definition.manifest.catalog.Length+" catalog pieces.");
  }
 }
}
#endif
