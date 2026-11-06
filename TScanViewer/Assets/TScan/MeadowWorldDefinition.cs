using System;
using UnityEngine;

namespace Steve.TScan {
 [Serializable] public class MeadowCell {public int col=8,row=8;}
 // A placed kit piece. yaw is degrees clockwise seen from above with north up: 0, 90, 180 or 270.
 [Serializable] public class MeadowPlacement {public string id,prototype;public int col,row,yaw;}
 // The role is assigned once, in the kit catalog; the backend independently checks that roles and blocking agree.
 [Serializable] public class MeadowCatalogEntry {public string prototype,name,role;public bool blocks;public int footprint=1;}   // footprint: cells covered per side (1, or 3 for large actors)
 [Serializable] public class MeadowManifest {
  public string schema="meadow-world-v3",world_id="steve_grid_v1";
  public int revision=1,columns=15,rows=15;
  public GridLandmark[] landmarks=Array.Empty<GridLandmark>();
  public MeadowCell spawn=new MeadowCell();
  public MeadowPlacement[] obstacles=Array.Empty<MeadowPlacement>();   // blocking pieces: walls, obstacles, closed doors
  public string[] floors=Array.Empty<string>();                         // one floor piece per cell, row by row from (1,1)
  public MeadowPlacement[] props=Array.Empty<MeadowPlacement>();       // walkable pieces: hazards, decor, open archways
  public MeadowCatalogEntry[] catalog=Array.Empty<MeadowCatalogEntry>();
 }

 [CreateAssetMenu(menuName="Steve/Meadow world definition")]
 public sealed class MeadowWorldDefinition:ScriptableObject {
  public MeadowManifest manifest=new MeadowManifest();
  public string ManifestJson=>JsonUtility.ToJson(manifest);
 }
}
