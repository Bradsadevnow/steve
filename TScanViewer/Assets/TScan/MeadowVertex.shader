Shader "Steve/MeadowVertex" {
 Properties { _BaseColor("Color",Color)=(1,1,1,1) _BaseMap("Base",2D)="white" {} _Cutoff("Cutoff",Float)=0.5 _Cull("Cull",Float)=0 }
 SubShader { Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque"} Cull Off
  Pass { Tags {"LightMode"="UniversalForward"} HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   struct A {float4 vertex:POSITION;float3 normal:NORMAL;float4 color:COLOR;};
   struct V {float4 pos:SV_POSITION;float3 normal:TEXCOORD0;float4 color:COLOR;};
   V vert(A v){V o;o.pos=TransformObjectToHClip(v.vertex.xyz);o.normal=TransformObjectToWorldNormal(v.normal);o.color=v.color;return o;}
   half4 frag(V i):SV_Target {Light l=GetMainLight();float d=saturate(dot(normalize(i.normal),l.direction));return half4(i.color.rgb*(.52+d*.55)*lerp(half3(1,1,1),l.color,.4),1);}
   ENDHLSL
  }
  UsePass "Universal Render Pipeline/Lit/ShadowCaster"
 }
}
