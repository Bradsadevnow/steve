// Generated from the adjacent Shader Graph. Regenerate with Tools > Moon Tribe > Generate Shader Variants.
// UI Toolkit uses its own rendering path; omit the SRP-only SubShader selection tag for Built-in.
Shader "Moon Tribe/Toolkit Runtime/VFX_Fill_Horisontal_Toolkit"
{
Properties
{
_MoonTime("Animation Time", Float) = 0

[NoScaleOffset]_MainTex("Main Texture", 2D) = "white" {}
Color_2E7FACD2("Big Noise Color", Color) = (0.4367552, 0, 1, 0)
Color_3B266F9B("Small Noise Color", Color) = (0, 0.6267567, 1, 0)
_Big_Particles_Color("Big Particles Color", Color) = (0.0235849, 0.8419742, 1, 1)
Vector1_D62A4478("Big Particles Size", Range(1, 5)) = 3
Vector1_3869530A("Big Particles Scroll Speed", Float) = -0.05
_Small_Particles_Color("Small Particles Color", Color) = (0.5729352, 0.9679446, 0.9716981, 1)
Vector1_31BC36D5("Small Particles Scroll Speed", Float) = -0.01
Vector1_EFFD96D3("Small Particles Size", Range(10, 25)) = 25
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
float4 Color_2E7FACD2;
float4 Color_3B266F9B;
float Vector1_D62A4478;
float Vector1_3869530A;
float Vector1_31BC36D5;
float Vector1_EFFD96D3;
float4 _Big_Particles_Color;
float4 _Small_Particles_Color;
UNITY_TEXTURE_STREAMING_DEBUG_VARS;
CBUFFER_END


// Object and Global properties
SAMPLER(SamplerState_Linear_Repeat);
TEXTURE2D(_MainTex);
SAMPLER(sampler_MainTex);

    // Graph Includes
    #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Hashes.hlsl"

    // Graph Functions
    
void Unity_TilingAndOffset_float(float2 UV, float2 Tiling, float2 Offset, out float2 Out)
{
    Out = UV * Tiling + Offset;
}

void Unity_Twirl_float(float2 UV, float2 Center, float Strength, float2 Offset, out float2 Out)
{
    float2 delta = UV - Center;
    float angle = Strength * length(delta);
    float x = cos(angle) * delta.x - sin(angle) * delta.y;
    float y = sin(angle) * delta.x + cos(angle) * delta.y;
    Out = float2(x + Center.x + Offset.x, y + Center.y + Offset.y);
}

void Unity_Multiply_float_float(float A, float B, out float Out)
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

void Unity_Power_float(float A, float B, out float Out)
{
    Out = pow(A, B);
}

void Unity_Multiply_float4_float4(float4 A, float4 B, out float4 Out)
{
Out = A * B;
}

void Unity_Add_float4(float4 A, float4 B, out float4 Out)
{
    Out = A + B;
}

void Unity_Clamp_float4(float4 In, float4 Min, float4 Max, out float4 Out)
{
    Out = clamp(In, Min, Max);
}

void Unity_Combine_float(float R, float G, float B, float A, out float4 RGBA, out float3 RGB, out float2 RG)
{
    RGBA = float4(R, G, B, A);
    RGB = float3(R, G, B);
    RG = float2(R, G);
}

void Unity_OneMinus_float(float In, out float Out)
{
    Out = 1 - In;
}

void Unity_Subtract_float(float A, float B, out float Out)
{
    Out = A - B;
}

void Unity_Clamp_float(float In, float Min, float Max, out float Out)
{
    Out = clamp(In, Min, Max);
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
UnityTexture2D _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D = UnityBuildTexture2DStructNoScale(_MainTex);
float4 _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4 = SAMPLE_TEXTURE2D(_Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.tex, _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.samplerstate, _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.GetTransformedUV(IN.uv0.xy) );
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_R_4_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.r;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_G_5_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.g;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_B_6_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.b;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_A_7_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.a;
float4 _Property_ed50a383efb277889152d5a97c8477da_Out_0_Vector4 = Color_2E7FACD2;
float2 _TilingAndOffset_29677ca1570a6783848fb1a2accc8829_Out_3_Vector2;
Unity_TilingAndOffset_float(IN.uv0.xy, float2 (2, 0.5), float2 (0, 0), _TilingAndOffset_29677ca1570a6783848fb1a2accc8829_Out_3_Vector2);
float2 _Twirl_d0b38691490fc58c868c908834ce46d7_Out_4_Vector2;
Unity_Twirl_float(_TilingAndOffset_29677ca1570a6783848fb1a2accc8829_Out_3_Vector2, float2 (0.5, 0.5), float(0.06), float2 (0, 0), _Twirl_d0b38691490fc58c868c908834ce46d7_Out_4_Vector2);
float _Multiply_a53916017d464b8eb97ab095b11d7e96_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, 1, _Multiply_a53916017d464b8eb97ab095b11d7e96_Out_2_Float);
float _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Out_3_Float;
float _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Cells_4_Float;
Unity_Voronoi_LegacySine_float(_Twirl_d0b38691490fc58c868c908834ce46d7_Out_4_Vector2, _Multiply_a53916017d464b8eb97ab095b11d7e96_Out_2_Float, float(4.18), _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Out_3_Float, _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Cells_4_Float);
float _Power_8fbb4fc95c43fa85a557eeba14ba0536_Out_2_Float;
Unity_Power_float(_Voronoi_643b106af3a65783a12e2e29f7d5bf08_Out_3_Float, float(6.37), _Power_8fbb4fc95c43fa85a557eeba14ba0536_Out_2_Float);
float4 _Multiply_628572dd08703381b01c86a23f597b03_Out_2_Vector4;
Unity_Multiply_float4_float4(_Property_ed50a383efb277889152d5a97c8477da_Out_0_Vector4, (_Power_8fbb4fc95c43fa85a557eeba14ba0536_Out_2_Float.xxxx), _Multiply_628572dd08703381b01c86a23f597b03_Out_2_Vector4);
float4 _Property_5ec4fe0839b9f5868cc613ab169cc7ca_Out_0_Vector4 = Color_3B266F9B;
float2 _TilingAndOffset_9833d1532bed118c9759f9e1a46e9e37_Out_3_Vector2;
Unity_TilingAndOffset_float(IN.uv0.xy, float2 (10, 2), float2 (0, 0), _TilingAndOffset_9833d1532bed118c9759f9e1a46e9e37_Out_3_Vector2);
float _Multiply_25879efc1a342788bbf6716de383633c_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, 1, _Multiply_25879efc1a342788bbf6716de383633c_Out_2_Float);
float _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Out_3_Float;
float _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Cells_4_Float;
Unity_Voronoi_LegacySine_float(_TilingAndOffset_9833d1532bed118c9759f9e1a46e9e37_Out_3_Vector2, _Multiply_25879efc1a342788bbf6716de383633c_Out_2_Float, float(3), _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Out_3_Float, _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Cells_4_Float);
float _Power_709ff8d3522eff8aa8f7dd275eaa21f6_Out_2_Float;
Unity_Power_float(_Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Out_3_Float, float(8.14), _Power_709ff8d3522eff8aa8f7dd275eaa21f6_Out_2_Float);
float4 _Multiply_a681a09ff007ea8db4f65ca0a3179ac0_Out_2_Vector4;
Unity_Multiply_float4_float4(_Property_5ec4fe0839b9f5868cc613ab169cc7ca_Out_0_Vector4, (_Power_709ff8d3522eff8aa8f7dd275eaa21f6_Out_2_Float.xxxx), _Multiply_a681a09ff007ea8db4f65ca0a3179ac0_Out_2_Vector4);
float4 _Add_f9d6929a09d446889ed03b58417eeec4_Out_2_Vector4;
Unity_Add_float4(_Multiply_628572dd08703381b01c86a23f597b03_Out_2_Vector4, _Multiply_a681a09ff007ea8db4f65ca0a3179ac0_Out_2_Vector4, _Add_f9d6929a09d446889ed03b58417eeec4_Out_2_Vector4);
float4 _Clamp_5793ac72d6ed3b8e8efbeae3d930add1_Out_3_Vector4;
Unity_Clamp_float4(_Add_f9d6929a09d446889ed03b58417eeec4_Out_2_Vector4, float4(0, 0, 0, 0), float4(1, 1, 1, 1), _Clamp_5793ac72d6ed3b8e8efbeae3d930add1_Out_3_Vector4);
float4 _Property_ba20e9bc69e9444b8e94863e89270fda_Out_0_Vector4 = _Big_Particles_Color;
float _Property_a971eda738625a8a9b0eff3aa4bc0106_Out_0_Float = Vector1_3869530A;
float _Multiply_727b6c8c0598cc8aad730ec315432408_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, _Property_a971eda738625a8a9b0eff3aa4bc0106_Out_0_Float, _Multiply_727b6c8c0598cc8aad730ec315432408_Out_2_Float);
float4 _Combine_9895650c59318b838d1e087f04dd0cd1_RGBA_4_Vector4;
float3 _Combine_9895650c59318b838d1e087f04dd0cd1_RGB_5_Vector3;
float2 _Combine_9895650c59318b838d1e087f04dd0cd1_RG_6_Vector2;
Unity_Combine_float(_Multiply_727b6c8c0598cc8aad730ec315432408_Out_2_Float, float(0), float(0), float(0), _Combine_9895650c59318b838d1e087f04dd0cd1_RGBA_4_Vector4, _Combine_9895650c59318b838d1e087f04dd0cd1_RGB_5_Vector3, _Combine_9895650c59318b838d1e087f04dd0cd1_RG_6_Vector2);
float2 _TilingAndOffset_933126f440b88589852445379e5aaa57_Out_3_Vector2;
Unity_TilingAndOffset_float(IN.uv0.xy, float2 (5, 1), _Combine_9895650c59318b838d1e087f04dd0cd1_RG_6_Vector2, _TilingAndOffset_933126f440b88589852445379e5aaa57_Out_3_Vector2);
float _Property_7be47cfae3be4f83a7f4d848fa8afdaf_Out_0_Float = Vector1_D62A4478;
float _Voronoi_f25be77906da3f84a452f2cf2bfadaff_Out_3_Float;
float _Voronoi_f25be77906da3f84a452f2cf2bfadaff_Cells_4_Float;
Unity_Voronoi_LegacySine_float(_TilingAndOffset_933126f440b88589852445379e5aaa57_Out_3_Vector2, float(5), _Property_7be47cfae3be4f83a7f4d848fa8afdaf_Out_0_Float, _Voronoi_f25be77906da3f84a452f2cf2bfadaff_Out_3_Float, _Voronoi_f25be77906da3f84a452f2cf2bfadaff_Cells_4_Float);
float _OneMinus_de456b46cbe0ce8c9ab24f2841560298_Out_1_Float;
Unity_OneMinus_float(_Voronoi_f25be77906da3f84a452f2cf2bfadaff_Out_3_Float, _OneMinus_de456b46cbe0ce8c9ab24f2841560298_Out_1_Float);
float _Subtract_467720d1ad08348d8008b653a2d425e2_Out_2_Float;
Unity_Subtract_float(_Voronoi_f25be77906da3f84a452f2cf2bfadaff_Out_3_Float, float(-0.58), _Subtract_467720d1ad08348d8008b653a2d425e2_Out_2_Float);
float _Subtract_a6acf3359e1e088ea2183dff849ce173_Out_2_Float;
Unity_Subtract_float(_OneMinus_de456b46cbe0ce8c9ab24f2841560298_Out_1_Float, _Subtract_467720d1ad08348d8008b653a2d425e2_Out_2_Float, _Subtract_a6acf3359e1e088ea2183dff849ce173_Out_2_Float);
float _Clamp_0cba2cbae071a883aa807ae162ed33e2_Out_3_Float;
Unity_Clamp_float(_Subtract_a6acf3359e1e088ea2183dff849ce173_Out_2_Float, float(0), float(1), _Clamp_0cba2cbae071a883aa807ae162ed33e2_Out_3_Float);
float4 _Multiply_795f867337cec181b0d692a6c63a638c_Out_2_Vector4;
Unity_Multiply_float4_float4(_Property_ba20e9bc69e9444b8e94863e89270fda_Out_0_Vector4, (_Clamp_0cba2cbae071a883aa807ae162ed33e2_Out_3_Float.xxxx), _Multiply_795f867337cec181b0d692a6c63a638c_Out_2_Vector4);
float4 _Property_1a231e5b2222408fa484a56ddd826fea_Out_0_Vector4 = _Small_Particles_Color;
float _Property_c4e8ef45d32dbe85ae1c06d57ccbda0c_Out_0_Float = Vector1_31BC36D5;
float _Multiply_d49e255bb5091f808812832569777f8c_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, _Property_c4e8ef45d32dbe85ae1c06d57ccbda0c_Out_0_Float, _Multiply_d49e255bb5091f808812832569777f8c_Out_2_Float);
float4 _Combine_cdabc96b911f2589a77e20c24bddea04_RGBA_4_Vector4;
float3 _Combine_cdabc96b911f2589a77e20c24bddea04_RGB_5_Vector3;
float2 _Combine_cdabc96b911f2589a77e20c24bddea04_RG_6_Vector2;
Unity_Combine_float(_Multiply_d49e255bb5091f808812832569777f8c_Out_2_Float, float(0), float(0), float(0), _Combine_cdabc96b911f2589a77e20c24bddea04_RGBA_4_Vector4, _Combine_cdabc96b911f2589a77e20c24bddea04_RGB_5_Vector3, _Combine_cdabc96b911f2589a77e20c24bddea04_RG_6_Vector2);
float2 _TilingAndOffset_c0a20bf69d01068fb6e9ffa2b1a65254_Out_3_Vector2;
Unity_TilingAndOffset_float(IN.uv0.xy, float2 (5, 1), _Combine_cdabc96b911f2589a77e20c24bddea04_RG_6_Vector2, _TilingAndOffset_c0a20bf69d01068fb6e9ffa2b1a65254_Out_3_Vector2);
float _Property_25410ddb74bf2d848c25c9075a169663_Out_0_Float = Vector1_EFFD96D3;
float _Voronoi_4014d69dcaa6578aa824b35ac916aef5_Out_3_Float;
float _Voronoi_4014d69dcaa6578aa824b35ac916aef5_Cells_4_Float;
Unity_Voronoi_LegacySine_float(_TilingAndOffset_c0a20bf69d01068fb6e9ffa2b1a65254_Out_3_Vector2, float(20), _Property_25410ddb74bf2d848c25c9075a169663_Out_0_Float, _Voronoi_4014d69dcaa6578aa824b35ac916aef5_Out_3_Float, _Voronoi_4014d69dcaa6578aa824b35ac916aef5_Cells_4_Float);
float _OneMinus_3f0e7774eb03b8889db0464a3e8e1c6e_Out_1_Float;
Unity_OneMinus_float(_Voronoi_4014d69dcaa6578aa824b35ac916aef5_Out_3_Float, _OneMinus_3f0e7774eb03b8889db0464a3e8e1c6e_Out_1_Float);
float _Subtract_60de4a7a8344d688a270af41c1b60021_Out_2_Float;
Unity_Subtract_float(_Voronoi_4014d69dcaa6578aa824b35ac916aef5_Out_3_Float, float(-0.58), _Subtract_60de4a7a8344d688a270af41c1b60021_Out_2_Float);
float _Subtract_fad42ed1957bb08a9ca2253b26bfa5b1_Out_2_Float;
Unity_Subtract_float(_OneMinus_3f0e7774eb03b8889db0464a3e8e1c6e_Out_1_Float, _Subtract_60de4a7a8344d688a270af41c1b60021_Out_2_Float, _Subtract_fad42ed1957bb08a9ca2253b26bfa5b1_Out_2_Float);
float _Clamp_170b935d3289208dbcce67d7014e3f9b_Out_3_Float;
Unity_Clamp_float(_Subtract_fad42ed1957bb08a9ca2253b26bfa5b1_Out_2_Float, float(0), float(1), _Clamp_170b935d3289208dbcce67d7014e3f9b_Out_3_Float);
float4 _Multiply_e9823298975e7a8e8c6f8f749adf844c_Out_2_Vector4;
Unity_Multiply_float4_float4(_Property_1a231e5b2222408fa484a56ddd826fea_Out_0_Vector4, (_Clamp_170b935d3289208dbcce67d7014e3f9b_Out_3_Float.xxxx), _Multiply_e9823298975e7a8e8c6f8f749adf844c_Out_2_Vector4);
float4 _Add_4febc2d3f0862281a150c85b8ccbb13a_Out_2_Vector4;
Unity_Add_float4(_Multiply_795f867337cec181b0d692a6c63a638c_Out_2_Vector4, _Multiply_e9823298975e7a8e8c6f8f749adf844c_Out_2_Vector4, _Add_4febc2d3f0862281a150c85b8ccbb13a_Out_2_Vector4);
float4 _Add_3449af12b5e97987850e124f209b2388_Out_2_Vector4;
Unity_Add_float4(_Clamp_5793ac72d6ed3b8e8efbeae3d930add1_Out_3_Vector4, _Add_4febc2d3f0862281a150c85b8ccbb13a_Out_2_Vector4, _Add_3449af12b5e97987850e124f209b2388_Out_2_Vector4);
float4 _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4;
Unity_Add_float4(_SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4, _Add_3449af12b5e97987850e124f209b2388_Out_2_Vector4, _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4);
float4 _Multiply_cfa9a6e1c63b9d84b2f45e9088360d9a_Out_2_Vector4;
Unity_Multiply_float4_float4(Color_b657c2d41146bd889c906abfab54d006, _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4, _Multiply_cfa9a6e1c63b9d84b2f45e9088360d9a_Out_2_Vector4);
surface.BaseColor = (_Multiply_cfa9a6e1c63b9d84b2f45e9088360d9a_Out_2_Vector4.xyz);
surface.Alpha = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_A_7_Float;
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