// Generated from the adjacent Shader Graph. Regenerate with Tools > Moon Tribe > Generate Shader Variants.
// UI Toolkit uses its own rendering path; omit the SRP-only SubShader selection tag for Built-in.
Shader "Moon Tribe/Toolkit Runtime/VFX_Fill_RadiallWave110_Toolkit"
{
Properties
{
_MoonTime("Animation Time", Float) = 0

[NoScaleOffset]_MainTex("Main Texture", 2D) = "white" {}
_Wave_Color("Wave Color", Color) = (0.5952742, 0.3176471, 0.8452041, 1)
Vector1_A04F513("Wave Speed", Range(-3, 3)) = 0.5
Vector1_81C2A44D("Wave Size", Float) = 30
Vector1_6B830020("Wave thickness", Range(0, 3)) = 1
Vector1_D62A4478("Particles Size", Range(1, 20)) = 5
Vector1_3869530A("Particles Scroll Speed", Float) = 10
_Particles_Color("Particles Color", Color) = (0.2688679, 1, 0.8157058, 1)
[HideInInspector][NoScaleOffset]unity_Lightmaps("unity_Lightmaps", 2DArray) = "" {}
[HideInInspector][NoScaleOffset]unity_LightmapsInd("unity_LightmapsInd", 2DArray) = "" {}
[HideInInspector][NoScaleOffset]unity_ShadowMasks("unity_ShadowMasks", 2DArray) = "" {}
}
SubShader
{
Tags
{

"RenderType"="Transparent"
"isCustomUITKShader"="true"
"Queue"="Transparent"
// DisableBatching: <None>
"ShaderGraphShader"="true"
"ShaderGraphTargetId"=""
"IgnoreProjector"="True"
"PreviewType"="Plane"
"CanUseSpriteAtlas"="True"
}

Pass
{
    Name "Default"
    Tags
    {
        // LightMode: <None>
    }

    // Render State
    Cull Off
Blend SrcAlpha OneMinusSrcAlpha, One OneMinusSrcAlpha
ZWrite Off

    // Debug
    // <None>

    // --------------------------------------------------
    // Pass

    HLSLPROGRAM

    // Pragmas
    #pragma target 3.5
#pragma vertex uie_custom_vert
#pragma fragment uie_custom_frag

    // Keywords
    #pragma multi_compile_local _ _UIE_FORCE_GAMMA
#pragma multi_compile_local _ _UIE_TEXTURE_SLOT_COUNT_4 _UIE_TEXTURE_SLOT_COUNT_2 _UIE_TEXTURE_SLOT_COUNT_1
#pragma multi_compile_local _ _UIE_RENDER_TYPE_SOLID _UIE_RENDER_TYPE_TEXTURE _UIE_RENDER_TYPE_TEXT _UIE_RENDER_TYPE_GRADIENT
    // GraphKeywords: <None>

    #define UITK_SHADERGRAPH

    // Defines
   #define _SURFACE_TYPE_TRANSPARENT 1
   #define ATTRIBUTES_NEED_TEXCOORD0
   #define ATTRIBUTES_NEED_TEXCOORD1
   #define ATTRIBUTES_NEED_TEXCOORD2
   #define ATTRIBUTES_NEED_TEXCOORD3
   #define ATTRIBUTES_NEED_COLOR
   #define VARYINGS_NEED_TEXCOORD0
   #define VARYINGS_NEED_TEXCOORD1
   #define VARYINGS_NEED_TEXCOORD3
   #define VARYINGS_NEED_COLOR
   #define FEATURES_GRAPH_VERTEX

#define REQUIRE_DEPTH_TEXTURE
#define REQUIRE_NORMAL_TEXTURE

   #define SHADERPASS SHADERPASS_CUSTOM_UI

   #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Color.hlsl"
#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Texture.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include_with_pragmas "Packages/com.unity.render-pipelines.core/ShaderLibrary/FoveatedRenderingKeywords.hlsl"
#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/FoveatedRendering.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Input.hlsl"
#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/TextureStack.hlsl"
#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/DebugMipmapStreamingMacros.hlsl"
#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/UnityInstancing.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/ShaderGraphFunctions.hlsl"
#include "Packages/com.unity.shadergraph/Editor/Generation/Targets/BuiltIn/ShaderLibrary/Shim/UIShim.hlsl"

    // --------------------------------------------------
    // Structs and Packing


    struct Attributes
{
 float3 positionOS : POSITION;
 float4 color : COLOR;
 float4 uv0 : TEXCOORD0;
 float4 uv1 : TEXCOORD1;
 float4 uv2 : TEXCOORD2;
 float4 uv3 : TEXCOORD3;
 float4 uv4 : TEXCOORD4;
 float4 uv5 : TEXCOORD5;
 float4 uv6 : TEXCOORD6;
 float4 uv7 : TEXCOORD7;
#if UNITY_ANY_INSTANCING_ENABLED || defined(ATTRIBUTES_NEED_INSTANCEID)
 uint instanceID : INSTANCEID_SEMANTIC;
#endif
};
struct SurfaceDescriptionInputs
{
 float4 color;
 float4 typeTexSettings;
 float2 textCoreLoc;
 float4 circle;
 float4 uvClip;
 float2 layoutUV;
 float4 uv0;
 float3 TimeParameters;
};
struct Varyings
{
 float4 positionCS : SV_POSITION;
 float4 texCoord0;
 float4 texCoord1;
 float4 texCoord3;
 float4 texCoord4;
 float4 color;
#if UNITY_ANY_INSTANCING_ENABLED || defined(VARYINGS_NEED_INSTANCEID)
 uint instanceID : CUSTOM_INSTANCE_ID;
#endif
#if (defined(UNITY_STEREO_MULTIVIEW_ENABLED)) || (defined(UNITY_STEREO_INSTANCING_ENABLED) && (defined(SHADER_API_GLES3) || defined(SHADER_API_GLCORE)))
 uint stereoTargetEyeIndexAsBlendIdx0 : BLENDINDICES0;
#endif
#if (defined(UNITY_STEREO_INSTANCING_ENABLED))
 uint stereoTargetEyeIndexAsRTArrayIdx : SV_RenderTargetArrayIndex;
#endif
};
struct VertexDescriptionInputs
{
 float4 vertexPosition;
 float4 vertexColor;
 float4 uv;
 float4 xformClipPages;
 float4 ids;
 float4 flags;
 float4 opacityColorPages;
 float4 settingIndex;
 float4 circle;
};
struct PackedVaryings
{
 float4 positionCS : SV_POSITION;
 float4 texCoord0 : INTERP0;
 float4 texCoord1 : INTERP1;
 float4 texCoord3 : INTERP2;
 float4 texCoord4 : INTERP3;
 float4 color : INTERP4;
#if UNITY_ANY_INSTANCING_ENABLED || defined(VARYINGS_NEED_INSTANCEID)
 uint instanceID : CUSTOM_INSTANCE_ID;
#endif
#if (defined(UNITY_STEREO_MULTIVIEW_ENABLED)) || (defined(UNITY_STEREO_INSTANCING_ENABLED) && (defined(SHADER_API_GLES3) || defined(SHADER_API_GLCORE)))
 uint stereoTargetEyeIndexAsBlendIdx0 : BLENDINDICES0;
#endif
#if (defined(UNITY_STEREO_INSTANCING_ENABLED))
 uint stereoTargetEyeIndexAsRTArrayIdx : SV_RenderTargetArrayIndex;
#endif
};

    PackedVaryings PackVaryings (Varyings input)
{
PackedVaryings output;
ZERO_INITIALIZE(PackedVaryings, output);
output.positionCS = input.positionCS;
output.texCoord0.xyzw = input.texCoord0;
output.texCoord1.xyzw = input.texCoord1;
output.texCoord3.xyzw = input.texCoord3;
output.texCoord4.xyzw = input.texCoord4;
output.color.xyzw = input.color;
#if UNITY_ANY_INSTANCING_ENABLED || defined(VARYINGS_NEED_INSTANCEID)
output.instanceID = input.instanceID;
#endif
#if (defined(UNITY_STEREO_MULTIVIEW_ENABLED)) || (defined(UNITY_STEREO_INSTANCING_ENABLED) && (defined(SHADER_API_GLES3) || defined(SHADER_API_GLCORE)))
output.stereoTargetEyeIndexAsBlendIdx0 = input.stereoTargetEyeIndexAsBlendIdx0;
#endif
#if (defined(UNITY_STEREO_INSTANCING_ENABLED))
output.stereoTargetEyeIndexAsRTArrayIdx = input.stereoTargetEyeIndexAsRTArrayIdx;
#endif
return output;
}

Varyings UnpackVaryings (PackedVaryings input)
{
Varyings output;
output.positionCS = input.positionCS;
output.texCoord0 = input.texCoord0.xyzw;
output.texCoord1 = input.texCoord1.xyzw;
output.texCoord3 = input.texCoord3.xyzw;
output.texCoord4 = input.texCoord4.xyzw;
output.color = input.color.xyzw;
#if UNITY_ANY_INSTANCING_ENABLED || defined(VARYINGS_NEED_INSTANCEID)
output.instanceID = input.instanceID;
#endif
#if (defined(UNITY_STEREO_MULTIVIEW_ENABLED)) || (defined(UNITY_STEREO_INSTANCING_ENABLED) && (defined(SHADER_API_GLES3) || defined(SHADER_API_GLCORE)))
output.stereoTargetEyeIndexAsBlendIdx0 = input.stereoTargetEyeIndexAsBlendIdx0;
#endif
#if (defined(UNITY_STEREO_INSTANCING_ENABLED))
output.stereoTargetEyeIndexAsRTArrayIdx = input.stereoTargetEyeIndexAsRTArrayIdx;
#endif
return output;
}


    // -- Property used by ScenePickingPass
    #ifdef SCENEPICKINGPASS
    float4 _SelectionID;
    #endif

    // -- Properties used by SceneSelectionPass
    #ifdef SCENESELECTIONPASS
    int _ObjectId;
    int _PassValue;
    #endif

    //UGUI has no keyword for when a renderer has "bloom", so its nessecary to hardcore it here, like all the base UI shaders.
    half4 _TextureSampleAdd;

    // --------------------------------------------------
    // Graph

    // Graph Properties
    CBUFFER_START(UnityPerMaterial)
float _MoonTime;
float4 _MainTex_TexelSize;
float Vector1_A04F513;
float Vector1_81C2A44D;
float Vector1_6B830020;
float Vector1_D62A4478;
float Vector1_3869530A;
float4 _Wave_Color;
float4 _Particles_Color;
UNITY_TEXTURE_STREAMING_DEBUG_VARS;
CBUFFER_END


// Object and Global properties
SAMPLER(SamplerState_Linear_Repeat);
TEXTURE2D(_MainTex);
SAMPLER(sampler_MainTex);

    // Graph Includes
    #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Hashes.hlsl"

    // Graph Functions
    
void Unity_Rotate_Radians_float(float2 UV, float2 Center, float Rotation, out float2 Out)
{
    UV -= Center;
    float s, c;
    sincos(Rotation, s, c);
    float3 r3 = float3(-s, c, s);
    float2 r1;
    r1.y = dot(UV, r3.xy);
    r1.x = dot(UV, r3.yz);
    Out = r1 + Center;
}

void Unity_PolarCoordinates_float(float2 UV, float2 Center, float RadialScale, float LengthScale, out float2 Out)
{
    float2 delta = UV - Center;
    float radius = length(delta) * 2 * RadialScale;
    float angle = atan2(delta.x, delta.y) * 1.0/6.28 * LengthScale;
    Out = float2(radius, angle);
}

void Unity_Add_float(float A, float B, out float Out)
{
    Out = A + B;
}

void Unity_OneMinus_float(float In, out float Out)
{
    Out = 1 - In;
}

void Unity_Multiply_float_float(float A, float B, out float Out)
{
Out = A * B;
}

void Unity_Combine_float(float R, float G, float B, float A, out float4 RGBA, out float3 RGB, out float2 RG)
{
    RGBA = float4(R, G, B, A);
    RGB = float3(R, G, B);
    RG = float2(R, G);
}

void Unity_TilingAndOffset_float(float2 UV, float2 Tiling, float2 Offset, out float2 Out)
{
    Out = UV * Tiling + Offset;
}

float Unity_SimpleNoise_ValueNoise_LegacySine_float (float2 uv)
{
float2 i = floor(uv);
float2 f = frac(uv);
f = f * f * (3.0 - 2.0 * f);
uv = abs(frac(uv) - 0.5);
float2 c0 = i + float2(0.0, 0.0);
float2 c1 = i + float2(1.0, 0.0);
float2 c2 = i + float2(0.0, 1.0);
float2 c3 = i + float2(1.0, 1.0);
float r0; Hash_LegacySine_2_1_float(c0, r0);
float r1; Hash_LegacySine_2_1_float(c1, r1);
float r2; Hash_LegacySine_2_1_float(c2, r2);
float r3; Hash_LegacySine_2_1_float(c3, r3);
float bottomOfGrid = lerp(r0, r1, f.x);
float topOfGrid = lerp(r2, r3, f.x);
float t = lerp(bottomOfGrid, topOfGrid, f.y);
return t;
}

void Unity_SimpleNoise_LegacySine_float(float2 UV, float Scale, out float Out)
{
float freq, amp;
Out = 0.0f;
freq = pow(2.0, float(0));
amp = pow(0.5, float(3-0));
Out += Unity_SimpleNoise_ValueNoise_LegacySine_float(float2(UV.xy*(Scale/freq)))*amp;
freq = pow(2.0, float(1));
amp = pow(0.5, float(3-1));
Out += Unity_SimpleNoise_ValueNoise_LegacySine_float(float2(UV.xy*(Scale/freq)))*amp;
freq = pow(2.0, float(2));
amp = pow(0.5, float(3-2));
Out += Unity_SimpleNoise_ValueNoise_LegacySine_float(float2(UV.xy*(Scale/freq)))*amp;
}

void Unity_Remap_float(float In, float2 InMinMax, float2 OutMinMax, out float Out)
{
    Out = OutMinMax.x + (In - InMinMax.x) * (OutMinMax.y - OutMinMax.x) / (InMinMax.y - InMinMax.x);
}

void Unity_Blend_Darken_float(float Base, float Blend, out float Out, float Opacity)
{
    Out = min(Blend, Base);
    Out = lerp(Base, Out, Opacity);
}

void Unity_Clamp_float(float In, float Min, float Max, out float Out)
{
    Out = clamp(In, Min, Max);
}

void Unity_Multiply_float4_float4(float4 A, float4 B, out float4 Out)
{
Out = A * B;
}

float2 Unity_Voronoi_RandomVector_LegacySine_float (float2 UV, float offset)
{
Hash_LegacySine_2_2_float(UV, UV);
return float2(sin(UV.y * offset), cos(UV.x * offset)) * 0.5 + 0.5;
}

void Unity_Voronoi_LegacySine_float(float2 UV, float AngleOffset, float CellDensity, out float Out, out float Cells)
{
float2 g = floor(UV * CellDensity);
float2 f = frac(UV * CellDensity);
float t = 8.0;
float3 res = float3(8.0, 0.0, 0.0);
for (int y = -1; y <= 1; y++)
{
for (int x = -1; x <= 1; x++)
{
float2 lattice = float2(x, y);
float2 offset = Unity_Voronoi_RandomVector_LegacySine_float(lattice + g, AngleOffset);
float d = distance(lattice + offset, f);
if (d < res.x)
{
res = float3(d, offset.x, offset.y);
Out = res.x;
Cells = res.y;
}
}
}
}

void Unity_Subtract_float(float A, float B, out float Out)
{
    Out = A - B;
}

void Unity_Subtract_float4(float4 A, float4 B, out float4 Out)
{
    Out = A - B;
}

void Unity_Power_float4(float4 A, float4 B, out float4 Out)
{
    Out = pow(A, B);
}

void Unity_Add_float4(float4 A, float4 B, out float4 Out)
{
    Out = A + B;
}

    /* WARNING: $splice Could not find named fragment 'CustomInterpolatorPreVertex' */

    // Graph Vertex
    struct VertexDescription
{
};

VertexDescription VertexDescriptionFunction(VertexDescriptionInputs IN)
{
VertexDescription description = (VertexDescription)0;
return description;
}

    /* WARNING: $splice Could not find named fragment 'CustomInterpolatorPreSurface' */

    // Graph Pixel
    struct SurfaceDescription
{
float3 BaseColor;
float Alpha;
};

SurfaceDescription SurfaceDescriptionFunction(SurfaceDescriptionInputs IN)
{
SurfaceDescription surface = (SurfaceDescription)0;
float4 Color_b657c2d41146bd889c906abfab54d006 = IsGammaSpace() ? float4(1, 1, 1, 1) : float4(SRGBToLinear(float3(1, 1, 1)), 1);
float4 _Property_bac26330935e46beb7233d52d0c9469d_Out_0_Vector4 = _Wave_Color;
float2 _Rotate_49702a6d869ac4858ce798314edbf28f_Out_3_Vector2;
Unity_Rotate_Radians_float(IN.uv0.xy, float2 (0.5, 0.5), float(3.1), _Rotate_49702a6d869ac4858ce798314edbf28f_Out_3_Vector2);
float2 _PolarCoordinates_0f775ef84a51008c826db8d61765a60f_Out_4_Vector2;
Unity_PolarCoordinates_float(_Rotate_49702a6d869ac4858ce798314edbf28f_Out_3_Vector2, float2 (0.5, 0.5), float(1), float(1), _PolarCoordinates_0f775ef84a51008c826db8d61765a60f_Out_4_Vector2);
float _Property_d9171d0ae41eee8c83571e31b83d5eae_Out_0_Float = Vector1_A04F513;
float _Add_198506dedeffbf87be65e4532bb6f4c6_Out_2_Float;
Unity_Add_float(_Property_d9171d0ae41eee8c83571e31b83d5eae_Out_0_Float, float(1), _Add_198506dedeffbf87be65e4532bb6f4c6_Out_2_Float);
float _OneMinus_73e74769a4353c8b9756cd20fc9eb0a2_Out_1_Float;
Unity_OneMinus_float(_Add_198506dedeffbf87be65e4532bb6f4c6_Out_2_Float, _OneMinus_73e74769a4353c8b9756cd20fc9eb0a2_Out_1_Float);
float _Multiply_a8cb66751927ae8b9e1f9d9b5e058fd1_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, _OneMinus_73e74769a4353c8b9756cd20fc9eb0a2_Out_1_Float, _Multiply_a8cb66751927ae8b9e1f9d9b5e058fd1_Out_2_Float);
float4 _Combine_6f4220045f621589904e713c1c82b088_RGBA_4_Vector4;
float3 _Combine_6f4220045f621589904e713c1c82b088_RGB_5_Vector3;
float2 _Combine_6f4220045f621589904e713c1c82b088_RG_6_Vector2;
Unity_Combine_float(_Multiply_a8cb66751927ae8b9e1f9d9b5e058fd1_Out_2_Float, float(0), float(0), float(0), _Combine_6f4220045f621589904e713c1c82b088_RGBA_4_Vector4, _Combine_6f4220045f621589904e713c1c82b088_RGB_5_Vector3, _Combine_6f4220045f621589904e713c1c82b088_RG_6_Vector2);
float2 _TilingAndOffset_7c7c585be18b08869c791c08f33ff772_Out_3_Vector2;
Unity_TilingAndOffset_float(_PolarCoordinates_0f775ef84a51008c826db8d61765a60f_Out_4_Vector2, float2 (1, 1), _Combine_6f4220045f621589904e713c1c82b088_RG_6_Vector2, _TilingAndOffset_7c7c585be18b08869c791c08f33ff772_Out_3_Vector2);
float _Property_ca7bc080879aa887a8f410da3d52dddd_Out_0_Float = Vector1_81C2A44D;
float _Add_c43bac18d95d0a84b89bd3cb0ddfe272_Out_2_Float;
Unity_Add_float(_Property_ca7bc080879aa887a8f410da3d52dddd_Out_0_Float, float(3), _Add_c43bac18d95d0a84b89bd3cb0ddfe272_Out_2_Float);
float _SimpleNoise_5ccbfd376983d78ab7dd215cc1782521_Out_2_Float;
Unity_SimpleNoise_LegacySine_float(_TilingAndOffset_7c7c585be18b08869c791c08f33ff772_Out_3_Vector2, _Add_c43bac18d95d0a84b89bd3cb0ddfe272_Out_2_Float, _SimpleNoise_5ccbfd376983d78ab7dd215cc1782521_Out_2_Float);
float _Property_44dadd5453d2278a8ce84126abff8150_Out_0_Float = Vector1_6B830020;
float4 _Combine_6d7a8883d9b03781971177b9f49f97da_RGBA_4_Vector4;
float3 _Combine_6d7a8883d9b03781971177b9f49f97da_RGB_5_Vector3;
float2 _Combine_6d7a8883d9b03781971177b9f49f97da_RG_6_Vector2;
Unity_Combine_float(float(-2.6), _Property_44dadd5453d2278a8ce84126abff8150_Out_0_Float, float(0), float(0), _Combine_6d7a8883d9b03781971177b9f49f97da_RGBA_4_Vector4, _Combine_6d7a8883d9b03781971177b9f49f97da_RGB_5_Vector3, _Combine_6d7a8883d9b03781971177b9f49f97da_RG_6_Vector2);
float _Remap_9443ad4267a2078db229541f9f423312_Out_3_Float;
Unity_Remap_float(_SimpleNoise_5ccbfd376983d78ab7dd215cc1782521_Out_2_Float, float2 (-1, 1), _Combine_6d7a8883d9b03781971177b9f49f97da_RG_6_Vector2, _Remap_9443ad4267a2078db229541f9f423312_Out_3_Float);
float2 _Rotate_c506cd46ededa183a92843083b3e7779_Out_3_Vector2;
Unity_Rotate_Radians_float(IN.uv0.xy, float2 (0.5, 0.5), float(0), _Rotate_c506cd46ededa183a92843083b3e7779_Out_3_Vector2);
float _Split_51a4718b4aa51e8bbdfe2ba5f7f4e243_R_1_Float = _Rotate_c506cd46ededa183a92843083b3e7779_Out_3_Vector2[0];
float _Split_51a4718b4aa51e8bbdfe2ba5f7f4e243_G_2_Float = _Rotate_c506cd46ededa183a92843083b3e7779_Out_3_Vector2[1];
float _Split_51a4718b4aa51e8bbdfe2ba5f7f4e243_B_3_Float = 0;
float _Split_51a4718b4aa51e8bbdfe2ba5f7f4e243_A_4_Float = 0;
float _Remap_43562bb6b29def8691ff2f9f98fc6f86_Out_3_Float;
Unity_Remap_float(_Split_51a4718b4aa51e8bbdfe2ba5f7f4e243_G_2_Float, float2 (-1, 1), float2 (-5.5, 2.53), _Remap_43562bb6b29def8691ff2f9f98fc6f86_Out_3_Float);
float _OneMinus_9d6e784697c8008cb5585d85605c585e_Out_1_Float;
Unity_OneMinus_float(_Remap_43562bb6b29def8691ff2f9f98fc6f86_Out_3_Float, _OneMinus_9d6e784697c8008cb5585d85605c585e_Out_1_Float);
float _Blend_16ccfe3c421df58084bf649b7b674ce5_Out_2_Float;
Unity_Blend_Darken_float(_Remap_9443ad4267a2078db229541f9f423312_Out_3_Float, _OneMinus_9d6e784697c8008cb5585d85605c585e_Out_1_Float, _Blend_16ccfe3c421df58084bf649b7b674ce5_Out_2_Float, float(1));
float _Clamp_5d7cbabff8ef4185b08f873bc895ce17_Out_3_Float;
Unity_Clamp_float(_Blend_16ccfe3c421df58084bf649b7b674ce5_Out_2_Float, float(0), float(1), _Clamp_5d7cbabff8ef4185b08f873bc895ce17_Out_3_Float);
float2 _PolarCoordinates_e5fa202159e6c68eb4e00eeca2b6b865_Out_4_Vector2;
Unity_PolarCoordinates_float(IN.uv0.xy, float2 (0.5, 0.5), float(1), float(1), _PolarCoordinates_e5fa202159e6c68eb4e00eeca2b6b865_Out_4_Vector2);
float2 _TilingAndOffset_af06c5a502ed688382e2f13415817a66_Out_3_Vector2;
Unity_TilingAndOffset_float(_PolarCoordinates_e5fa202159e6c68eb4e00eeca2b6b865_Out_4_Vector2, float2 (1, 1), _Combine_6f4220045f621589904e713c1c82b088_RG_6_Vector2, _TilingAndOffset_af06c5a502ed688382e2f13415817a66_Out_3_Vector2);
float _SimpleNoise_e95d1786886a0f84bc36d2a3de783263_Out_2_Float;
Unity_SimpleNoise_LegacySine_float(_TilingAndOffset_af06c5a502ed688382e2f13415817a66_Out_3_Vector2, _Property_ca7bc080879aa887a8f410da3d52dddd_Out_0_Float, _SimpleNoise_e95d1786886a0f84bc36d2a3de783263_Out_2_Float);
float _Remap_5e441d4e345783888e1204b86fbb0cfd_Out_3_Float;
Unity_Remap_float(_SimpleNoise_e95d1786886a0f84bc36d2a3de783263_Out_2_Float, float2 (-1, 1), _Combine_6d7a8883d9b03781971177b9f49f97da_RG_6_Vector2, _Remap_5e441d4e345783888e1204b86fbb0cfd_Out_3_Float);
float _Blend_1e35f949cf72ae8db2e8f40cfa7f2b26_Out_2_Float;
Unity_Blend_Darken_float(_Remap_43562bb6b29def8691ff2f9f98fc6f86_Out_3_Float, _Remap_5e441d4e345783888e1204b86fbb0cfd_Out_3_Float, _Blend_1e35f949cf72ae8db2e8f40cfa7f2b26_Out_2_Float, float(1));
float _Clamp_6542024923d831878eaceef8a1a8bdb3_Out_3_Float;
Unity_Clamp_float(_Blend_1e35f949cf72ae8db2e8f40cfa7f2b26_Out_2_Float, float(0), float(1), _Clamp_6542024923d831878eaceef8a1a8bdb3_Out_3_Float);
float _Add_58c7a621b8033186857b4e27661c3192_Out_2_Float;
Unity_Add_float(_Clamp_5d7cbabff8ef4185b08f873bc895ce17_Out_3_Float, _Clamp_6542024923d831878eaceef8a1a8bdb3_Out_3_Float, _Add_58c7a621b8033186857b4e27661c3192_Out_2_Float);
float2 _PolarCoordinates_0e915ca85fa76a8fa9920f999f7bcc8b_Out_4_Vector2;
Unity_PolarCoordinates_float(IN.uv0.xy, float2 (0.5, 0.5), float(1), float(1), _PolarCoordinates_0e915ca85fa76a8fa9920f999f7bcc8b_Out_4_Vector2);
float _Split_4d63dfb74680478487a386ee27b80d3e_R_1_Float = _PolarCoordinates_0e915ca85fa76a8fa9920f999f7bcc8b_Out_4_Vector2[0];
float _Split_4d63dfb74680478487a386ee27b80d3e_G_2_Float = _PolarCoordinates_0e915ca85fa76a8fa9920f999f7bcc8b_Out_4_Vector2[1];
float _Split_4d63dfb74680478487a386ee27b80d3e_B_3_Float = 0;
float _Split_4d63dfb74680478487a386ee27b80d3e_A_4_Float = 0;
float _Remap_7cfac1e8d644308eab062b71a73e9dae_Out_3_Float;
Unity_Remap_float(_Split_4d63dfb74680478487a386ee27b80d3e_R_1_Float, float2 (-1, 1), float2 (-2.48, 2.09), _Remap_7cfac1e8d644308eab062b71a73e9dae_Out_3_Float);
float _Clamp_e0baf7559e41be8fa814c896b4be962e_Out_3_Float;
Unity_Clamp_float(_Remap_7cfac1e8d644308eab062b71a73e9dae_Out_3_Float, float(0), float(1), _Clamp_e0baf7559e41be8fa814c896b4be962e_Out_3_Float);
float _Multiply_bd2221092af7c7898093409edff924d2_Out_2_Float;
Unity_Multiply_float_float(_Add_58c7a621b8033186857b4e27661c3192_Out_2_Float, _Clamp_e0baf7559e41be8fa814c896b4be962e_Out_3_Float, _Multiply_bd2221092af7c7898093409edff924d2_Out_2_Float);
float4 _Multiply_22dcb96063d5e288a6421806b4dbd1f9_Out_2_Vector4;
Unity_Multiply_float4_float4(_Property_bac26330935e46beb7233d52d0c9469d_Out_0_Vector4, (_Multiply_bd2221092af7c7898093409edff924d2_Out_2_Float.xxxx), _Multiply_22dcb96063d5e288a6421806b4dbd1f9_Out_2_Vector4);
UnityTexture2D _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D = UnityBuildTexture2DStructNoScale(_MainTex);
float4 _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4 = SAMPLE_TEXTURE2D(_Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.tex, _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.samplerstate, _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.GetTransformedUV(IN.uv0.xy) );
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_R_4_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.r;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_G_5_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.g;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_B_6_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.b;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_A_7_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.a;
float2 _TilingAndOffset_dcf12e42def87685b468a2f8006f7454_Out_3_Vector2;
Unity_TilingAndOffset_float(IN.uv0.xy, float2 (1, 1), float2 (0, 0), _TilingAndOffset_dcf12e42def87685b468a2f8006f7454_Out_3_Vector2);
float2 _PolarCoordinates_31649abd163f2489866e83af0c6e7f7c_Out_4_Vector2;
Unity_PolarCoordinates_float(_TilingAndOffset_dcf12e42def87685b468a2f8006f7454_Out_3_Vector2, float2 (0.5, 0.5), float(0.72), float(10.27), _PolarCoordinates_31649abd163f2489866e83af0c6e7f7c_Out_4_Vector2);
float _Split_9c28971418bd438f8970f496c412a758_R_1_Float = _PolarCoordinates_31649abd163f2489866e83af0c6e7f7c_Out_4_Vector2[0];
float _Split_9c28971418bd438f8970f496c412a758_G_2_Float = _PolarCoordinates_31649abd163f2489866e83af0c6e7f7c_Out_4_Vector2[1];
float _Split_9c28971418bd438f8970f496c412a758_B_3_Float = 0;
float _Split_9c28971418bd438f8970f496c412a758_A_4_Float = 0;
float _Multiply_cfa130a48a22838d9aa47d0b4b3937c4_Out_2_Float;
Unity_Multiply_float_float(1, _Split_9c28971418bd438f8970f496c412a758_R_1_Float, _Multiply_cfa130a48a22838d9aa47d0b4b3937c4_Out_2_Float);
float _Remap_7b39056422fb988596b412521ce19ebc_Out_3_Float;
Unity_Remap_float(_Multiply_cfa130a48a22838d9aa47d0b4b3937c4_Out_2_Float, float2 (-1, 1), float2 (-2.86, 1.58), _Remap_7b39056422fb988596b412521ce19ebc_Out_3_Float);
float _Property_5be6861a6a8c59888a95c9e3cb84fa00_Out_0_Float = Vector1_3869530A;
float _Multiply_6310839c18e37a8eac69451d443c5ae6_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, _Property_5be6861a6a8c59888a95c9e3cb84fa00_Out_0_Float, _Multiply_6310839c18e37a8eac69451d443c5ae6_Out_2_Float);
float _Property_ace2a909272b948599b81efe98edeec4_Out_0_Float = Vector1_D62A4478;
float _Voronoi_75b8a7d41513fe8bbfd59fed372bec02_Out_3_Float;
float _Voronoi_75b8a7d41513fe8bbfd59fed372bec02_Cells_4_Float;
Unity_Voronoi_LegacySine_float(_PolarCoordinates_31649abd163f2489866e83af0c6e7f7c_Out_4_Vector2, _Multiply_6310839c18e37a8eac69451d443c5ae6_Out_2_Float, _Property_ace2a909272b948599b81efe98edeec4_Out_0_Float, _Voronoi_75b8a7d41513fe8bbfd59fed372bec02_Out_3_Float, _Voronoi_75b8a7d41513fe8bbfd59fed372bec02_Cells_4_Float);
float _OneMinus_9a83b9464f33088d993f0ad77b1b9336_Out_1_Float;
Unity_OneMinus_float(_Voronoi_75b8a7d41513fe8bbfd59fed372bec02_Out_3_Float, _OneMinus_9a83b9464f33088d993f0ad77b1b9336_Out_1_Float);
float _Subtract_5d9114998460f185b6c857663515e2c3_Out_2_Float;
Unity_Subtract_float(_Voronoi_75b8a7d41513fe8bbfd59fed372bec02_Out_3_Float, float(-0.27), _Subtract_5d9114998460f185b6c857663515e2c3_Out_2_Float);
float _Subtract_834842c5285f67829bbab4dc75d0dfe3_Out_2_Float;
Unity_Subtract_float(_OneMinus_9a83b9464f33088d993f0ad77b1b9336_Out_1_Float, _Subtract_5d9114998460f185b6c857663515e2c3_Out_2_Float, _Subtract_834842c5285f67829bbab4dc75d0dfe3_Out_2_Float);
float _Clamp_150c512143751f8fa4b32b9585cb3e89_Out_3_Float;
Unity_Clamp_float(_Subtract_834842c5285f67829bbab4dc75d0dfe3_Out_2_Float, float(0), float(1), _Clamp_150c512143751f8fa4b32b9585cb3e89_Out_3_Float);
float _Multiply_9e6fbcbd9907838a88730c10355daeef_Out_2_Float;
Unity_Multiply_float_float(_Remap_7b39056422fb988596b412521ce19ebc_Out_3_Float, _Clamp_150c512143751f8fa4b32b9585cb3e89_Out_3_Float, _Multiply_9e6fbcbd9907838a88730c10355daeef_Out_2_Float);
float _Clamp_1ee5cf7c3414958aaeb1859cac38397f_Out_3_Float;
Unity_Clamp_float(_Multiply_9e6fbcbd9907838a88730c10355daeef_Out_2_Float, float(0), float(1), _Clamp_1ee5cf7c3414958aaeb1859cac38397f_Out_3_Float);
float4 _Subtract_3311bac82a47608ea0d4b94dedee04dd_Out_2_Vector4;
Unity_Subtract_float4(_SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4, (_Clamp_1ee5cf7c3414958aaeb1859cac38397f_Out_3_Float.xxxx), _Subtract_3311bac82a47608ea0d4b94dedee04dd_Out_2_Vector4);
float4 _Property_c83283bf5a454498868abf4d86e962b2_Out_0_Vector4 = _Particles_Color;
float4 _Multiply_68a3cd7e99e43187913c901a595f5dd8_Out_2_Vector4;
Unity_Multiply_float4_float4(_Property_c83283bf5a454498868abf4d86e962b2_Out_0_Vector4, (_Clamp_1ee5cf7c3414958aaeb1859cac38397f_Out_3_Float.xxxx), _Multiply_68a3cd7e99e43187913c901a595f5dd8_Out_2_Vector4);
float4 _Power_8828dfce38ac2d8f80a43beb3101959f_Out_2_Vector4;
Unity_Power_float4(_Multiply_68a3cd7e99e43187913c901a595f5dd8_Out_2_Vector4, float4(0.6, 0.6, 0.6, 0.7), _Power_8828dfce38ac2d8f80a43beb3101959f_Out_2_Vector4);
float4 _Add_337b6146683c87898186ad76f95b06f6_Out_2_Vector4;
Unity_Add_float4(_Subtract_3311bac82a47608ea0d4b94dedee04dd_Out_2_Vector4, _Power_8828dfce38ac2d8f80a43beb3101959f_Out_2_Vector4, _Add_337b6146683c87898186ad76f95b06f6_Out_2_Vector4);
float4 _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4;
Unity_Add_float4(_Add_337b6146683c87898186ad76f95b06f6_Out_2_Vector4, _Multiply_68a3cd7e99e43187913c901a595f5dd8_Out_2_Vector4, _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4);
float4 _Add_cb640af5fd2e4b88889279f9e58abf17_Out_2_Vector4;
Unity_Add_float4(_Multiply_22dcb96063d5e288a6421806b4dbd1f9_Out_2_Vector4, _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4, _Add_cb640af5fd2e4b88889279f9e58abf17_Out_2_Vector4);
float4 _Multiply_cfa9a6e1c63b9d84b2f45e9088360d9a_Out_2_Vector4;
Unity_Multiply_float4_float4(Color_b657c2d41146bd889c906abfab54d006, _Add_cb640af5fd2e4b88889279f9e58abf17_Out_2_Vector4, _Multiply_cfa9a6e1c63b9d84b2f45e9088360d9a_Out_2_Vector4);
UnityTexture2D _Property_77b6f1783172b9859a7365704d12d6fd_Out_0_Texture2D = UnityBuildTexture2DStructNoScale(_MainTex);
float4 _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_RGBA_0_Vector4 = SAMPLE_TEXTURE2D(_Property_77b6f1783172b9859a7365704d12d6fd_Out_0_Texture2D.tex, _Property_77b6f1783172b9859a7365704d12d6fd_Out_0_Texture2D.samplerstate, _Property_77b6f1783172b9859a7365704d12d6fd_Out_0_Texture2D.GetTransformedUV(IN.uv0.xy) );
float _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_R_4_Float = _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_RGBA_0_Vector4.r;
float _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_G_5_Float = _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_RGBA_0_Vector4.g;
float _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_B_6_Float = _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_RGBA_0_Vector4.b;
float _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_A_7_Float = _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_RGBA_0_Vector4.a;
surface.BaseColor = (_Multiply_cfa9a6e1c63b9d84b2f45e9088360d9a_Out_2_Vector4.xyz);
surface.Alpha = _SampleTexture2D_3d128f917fd0b882814caab44ca7e337_A_7_Float;
surface.BaseColor *= IN.color.rgb; surface.Alpha *= IN.color.a; return surface;
}

    // --------------------------------------------------
    // Build Graph Inputs

    VertexDescriptionInputs BuildVertexDescriptionInputs(Attributes input)
{
    VertexDescriptionInputs output;
    ZERO_INITIALIZE(VertexDescriptionInputs, output);

#if UNITY_ANY_INSTANCING_ENABLED
#else // TODO: XR support for procedural instancing because in this case UNITY_ANY_INSTANCING_ENABLED is not defined and instanceID is incorrect.
#endif

    return output;
}
    SurfaceDescriptionInputs BuildSurfaceDescriptionInputs(Varyings input)
{
    SurfaceDescriptionInputs output;
    ZERO_INITIALIZE(SurfaceDescriptionInputs, output);
output.color=input.color; output.typeTexSettings=input.texCoord1; output.uvClip=input.texCoord0; output.circle=input.texCoord4; output.textCoreLoc=input.texCoord3.xy; output.layoutUV=input.texCoord3.zw;

    /* WARNING: $splice Could not find named fragment 'CustomInterpolatorCopyToSDI' */






    #if UNITY_UV_STARTS_AT_TOP
    #else
    #endif



#if defined(UNITY_UIE_INCLUDED)
    output.uv0 =                                        float4(input.texCoord0.x, input.texCoord0.y, 0, 0);
#else
    output.uv0 =                                        input.texCoord0;
#endif
    

    
    
#if UNITY_ANY_INSTANCING_ENABLED
#else // TODO: XR support for procedural instancing because in this case UNITY_ANY_INSTANCING_ENABLED is not defined and instanceID is incorrect.
#endif
    output.TimeParameters =                             float3(_MoonTime, sin(_MoonTime), cos(_MoonTime)); // This is mainly for LW as HD overwrite this value
#if defined(SHADER_STAGE_FRAGMENT) && defined(VARYINGS_NEED_CULLFACE)
#define BUILD_SURFACE_DESCRIPTION_INPUTS_OUTPUT_FACESIGN                output.FaceSign =                                   IS_FRONT_VFACE(input.cullFace, true, false);
#else
#define BUILD_SURFACE_DESCRIPTION_INPUTS_OUTPUT_FACESIGN
#endif
#undef BUILD_SURFACE_DESCRIPTION_INPUTS_OUTPUT_FACESIGN

    return output;
}

    // --------------------------------------------------
    // Main

    #include "Packages/com.unity.render-pipelines.universal/Editor/ShaderGraph/Includes/UITKPass.hlsl"

    ENDHLSL
}
}
CustomEditor "UnityEditor.ShaderGraph.GenericShaderGraphMaterialGUI"
FallBack off
}