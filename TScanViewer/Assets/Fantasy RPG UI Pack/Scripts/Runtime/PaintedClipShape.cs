using UnityEngine;
namespace MoonTribe.UI
{
    // Opaque horizontal spans of the authored resource background, sampled top to bottom.
    public class PaintedClipShape : ScriptableObject
    {
        public Vector2[] spans;
        public Vector2 At(float y)
        {
            if(spans==null || spans.Length==0 || y<0 || y>1) return new Vector2(1,0);
            float index=y*(spans.Length-1); int a=Mathf.FloorToInt(index), b=Mathf.Min(a+1,spans.Length-1);
            if(spans[a].x>spans[a].y || spans[b].x>spans[b].y) return new Vector2(1,0);
            return Vector2.Lerp(spans[a],spans[b],index-a);
        }
    }
}
