// Generated from the adjacent Shader Graph. Regenerate with Tools > Moon Tribe > Generate Shader Variants.
// UI Toolkit uses its own rendering path; omit the SRP-only SubShader selection tag for Built-in.
Shader "Moon Tribe/Toolkit Runtime/VFX_Fill_Radial_Toolkit"
{
Properties
{
_MoonTime("Animation Time", Float) = 0

[NoScaleOffset]_MainTex("Main Texture", 2D) = "white" {}
[NoScaleOffset]Texture2D_7EF502D7("Particles Texture", 2D) = "white" {}
_Particles_Color("Particles Color", Color) = (1, 0.7951086, 0, 1)
Vector1_79A9E2DA("Particles Twirl speed", Float) = 0.5
_Color_Big_Noise("Color Big Noise", Color) = (0.9811321, 0.3841225, 0.3841225, 1)
Vector1_CF3ADA02("Big Noise Size", Range(1, 5)) = 4
Vector1_436D2CD7("Big Noise Scroll Speed", Float) = 1
_Color_Small_Noise("Color Small Noise", Color) = (1, 0.4078432, 0, 1)
Vector1_832412A8("Small Noise Size", Range(8, 15)) = 10
Vector1_3067A95E("Small Noise Scroll Speed", Float) = 1
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
float4 Texture2D_7EF502D7_TexelSize;
float Vector1_79A9E2DA;
float Vector1_CF3ADA02;
float Vector1_436D2CD7;
float Vector1_832412A8;
float Vector1_3067A95E;
float4 _Particles_Color;
float4 _Color_Big_Noise;
float4 _Color_Small_Noise;
UNITY_TEXTURE_STREAMING_DEBUG_VARS;
CBUFFER_END


// Object and Global properties
SAMPLER(SamplerState_Linear_Repeat);
TEXTURE2D(_MainTex);
SAMPLER(sampler_MainTex);
TEXTURE2D(Texture2D_7EF502D7);
SAMPLER(samplerTexture2D_7EF502D7);

    // Graph Includes
    #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Hashes.hlsl"

    // Graph Functions
    
void Unity_Multiply_float_float(float A, float B, out float Out)
{
Out = A * B;
}

void Unity_Twirl_float(float2 UV, float2 Center, float Strength, float2 Offset, out float2 Out)
{
    float2 delta = UV - Center;
    float angle = Strength * length(delta);
    float x = cos(angle) * delta.x - sin(angle) * delta.y;
    float y = sin(angle) * delta.x + cos(angle) * delta.y;
    Out = float2(x + Center.x + Offset.x, y + Center.y + Offset.y);
}

void Unity_Multiply_float4_float4(float4 A, float4 B, out float4 Out)
{
Out = A * B;
}

void Unity_PolarCoordinates_float(float2 UV, float2 Center, float RadialScale, float LengthScale, out float2 Out)
{
    float2 delta = UV - Center;
    float radius = length(delta) * 2 * RadialScale;
    float angle = atan2(delta.x, delta.y) * 1.0/6.28 * LengthScale;
    Out = float2(radius, angle);
}

void Unity_Power_float(float A, float B, out float Out)
{
    Out = pow(A, B);
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

void Unity_Add_float(float A, float B, out float Out)
{
    Out = A + B;
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

void Unity_Clamp_float4(float4 In, float4 Min, float4 Max, out float4 Out)
{
    Out = clamp(In, Min, Max);
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
float4 Color_6c9e3069fc3b4e8e99792649df9fe6a1 = IsGammaSpace() ? float4(1, 1, 1, 1) : float4(SRGBToLinear(float3(1, 1, 1)), 1);
UnityTexture2D _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D = UnityBuildTexture2DStructNoScale(_MainTex);
float4 _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4 = SAMPLE_TEXTURE2D(_Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.tex, _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.samplerstate, _Property_921b893163870a8f9178c1a8effab239_Out_0_Texture2D.GetTransformedUV(IN.uv0.xy) );
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_R_4_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.r;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_G_5_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.g;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_B_6_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.b;
float _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_A_7_Float = _SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4.a;
UnityTexture2D _Property_39a38c1c8f102585a100f75f1173c1f9_Out_0_Texture2D = UnityBuildTexture2DStructNoScale(Texture2D_7EF502D7);
float _Property_b472cb7e0e0bb28391de8039552e50e5_Out_0_Float = Vector1_79A9E2DA;
float _Multiply_4e145ba49b409c8e8fd1c59a1de524c7_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.y, _Property_b472cb7e0e0bb28391de8039552e50e5_Out_0_Float, _Multiply_4e145ba49b409c8e8fd1c59a1de524c7_Out_2_Float);
float2 _Twirl_01938dda710a7b8b9f2be6f7af34338c_Out_4_Vector2;
Unity_Twirl_float(IN.uv0.xy, float2 (0.5, 0.5), _Multiply_4e145ba49b409c8e8fd1c59a1de524c7_Out_2_Float, float2 (0, 0), _Twirl_01938dda710a7b8b9f2be6f7af34338c_Out_4_Vector2);
float4 _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_RGBA_0_Vector4 = SAMPLE_TEXTURE2D(_Property_39a38c1c8f102585a100f75f1173c1f9_Out_0_Texture2D.tex, _Property_39a38c1c8f102585a100f75f1173c1f9_Out_0_Texture2D.samplerstate, _Property_39a38c1c8f102585a100f75f1173c1f9_Out_0_Texture2D.GetTransformedUV(_Twirl_01938dda710a7b8b9f2be6f7af34338c_Out_4_Vector2) );
float _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_R_4_Float = _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_RGBA_0_Vector4.r;
float _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_G_5_Float = _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_RGBA_0_Vector4.g;
float _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_B_6_Float = _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_RGBA_0_Vector4.b;
float _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_A_7_Float = _SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_RGBA_0_Vector4.a;
float4 _Property_2cc8ea8105fb4f51a1a6df51be4fe9f2_Out_0_Vector4 = _Particles_Color;
float4 _Multiply_304523a3ba1eb5849984e8aa16168284_Out_2_Vector4;
Unity_Multiply_float4_float4(_SampleTexture2D_c7b42442b9662f81b97cfca4f8b36bfb_RGBA_0_Vector4, _Property_2cc8ea8105fb4f51a1a6df51be4fe9f2_Out_0_Vector4, _Multiply_304523a3ba1eb5849984e8aa16168284_Out_2_Vector4);
float2 _PolarCoordinates_797f756909c2e58ba894ff2dc1d1b410_Out_4_Vector2;
Unity_PolarCoordinates_float(IN.uv0.xy, float2 (0.5, 0.5), float(1), float(1), _PolarCoordinates_797f756909c2e58ba894ff2dc1d1b410_Out_4_Vector2);
float _Split_ef5e21a8d947858a8f1db7a92a1e30b7_R_1_Float = _PolarCoordinates_797f756909c2e58ba894ff2dc1d1b410_Out_4_Vector2[0];
float _Split_ef5e21a8d947858a8f1db7a92a1e30b7_G_2_Float = _PolarCoordinates_797f756909c2e58ba894ff2dc1d1b410_Out_4_Vector2[1];
float _Split_ef5e21a8d947858a8f1db7a92a1e30b7_B_3_Float = 0;
float _Split_ef5e21a8d947858a8f1db7a92a1e30b7_A_4_Float = 0;
float _Power_bc21c7182eaadb848854224c773cbdc4_Out_2_Float;
Unity_Power_float(_Split_ef5e21a8d947858a8f1db7a92a1e30b7_R_1_Float, float(2), _Power_bc21c7182eaadb848854224c773cbdc4_Out_2_Float);
float _OneMinus_c99f6edd7d189380bb156f9d039f6426_Out_1_Float;
Unity_OneMinus_float(_Power_bc21c7182eaadb848854224c773cbdc4_Out_2_Float, _OneMinus_c99f6edd7d189380bb156f9d039f6426_Out_1_Float);
float _Subtract_c4503b0e91a33a8ca13815bea93dbba7_Out_2_Float;
Unity_Subtract_float(_OneMinus_c99f6edd7d189380bb156f9d039f6426_Out_1_Float, float(-0.44), _Subtract_c4503b0e91a33a8ca13815bea93dbba7_Out_2_Float);
float _Clamp_8994f7759c610784ba46331d55ef5e5a_Out_3_Float;
Unity_Clamp_float(_Subtract_c4503b0e91a33a8ca13815bea93dbba7_Out_2_Float, float(-0.13), float(0.87), _Clamp_8994f7759c610784ba46331d55ef5e5a_Out_3_Float);
float _Clamp_dbfb4bdc5c1ab388ac15a0647bf2dcf6_Out_3_Float;
Unity_Clamp_float(_OneMinus_c99f6edd7d189380bb156f9d039f6426_Out_1_Float, float(0.43), float(1.03), _Clamp_dbfb4bdc5c1ab388ac15a0647bf2dcf6_Out_3_Float);
float _Subtract_f6e4aef3b348b78dabda90ce2c5b9226_Out_2_Float;
Unity_Subtract_float(_Clamp_8994f7759c610784ba46331d55ef5e5a_Out_3_Float, _Clamp_dbfb4bdc5c1ab388ac15a0647bf2dcf6_Out_3_Float, _Subtract_f6e4aef3b348b78dabda90ce2c5b9226_Out_2_Float);
float _Add_a5ec627d0d171588b40fab13000f0407_Out_2_Float;
Unity_Add_float(_Subtract_f6e4aef3b348b78dabda90ce2c5b9226_Out_2_Float, _Subtract_f6e4aef3b348b78dabda90ce2c5b9226_Out_2_Float, _Add_a5ec627d0d171588b40fab13000f0407_Out_2_Float);
float _Add_cde0c1b47da0bd88b4a89f563a1a98fa_Out_2_Float;
Unity_Add_float(_Add_a5ec627d0d171588b40fab13000f0407_Out_2_Float, _Add_a5ec627d0d171588b40fab13000f0407_Out_2_Float, _Add_cde0c1b47da0bd88b4a89f563a1a98fa_Out_2_Float);
float4 _Multiply_929d0e10afdf118191dca672449de841_Out_2_Vector4;
Unity_Multiply_float4_float4(_Multiply_304523a3ba1eb5849984e8aa16168284_Out_2_Vector4, (_Add_cde0c1b47da0bd88b4a89f563a1a98fa_Out_2_Float.xxxx), _Multiply_929d0e10afdf118191dca672449de841_Out_2_Vector4);
float4 _Property_6f505a52783e410ba93f48a53098d428_Out_0_Vector4 = _Color_Big_Noise;
float2 _Twirl_d0b38691490fc58c868c908834ce46d7_Out_4_Vector2;
Unity_Twirl_float(IN.uv0.xy, float2 (0.5, 0.5), float(2.77), float2 (0, 0.9), _Twirl_d0b38691490fc58c868c908834ce46d7_Out_4_Vector2);
float _Property_e87f5bc17d6a618cb1b43131c017ee30_Out_0_Float = Vector1_436D2CD7;
float _Multiply_a53916017d464b8eb97ab095b11d7e96_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, _Property_e87f5bc17d6a618cb1b43131c017ee30_Out_0_Float, _Multiply_a53916017d464b8eb97ab095b11d7e96_Out_2_Float);
float _Property_839da0d3f640e782a85d3899ec1cd09b_Out_0_Float = Vector1_CF3ADA02;
float _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Out_3_Float;
float _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Cells_4_Float;
Unity_Voronoi_LegacySine_float(_Twirl_d0b38691490fc58c868c908834ce46d7_Out_4_Vector2, _Multiply_a53916017d464b8eb97ab095b11d7e96_Out_2_Float, _Property_839da0d3f640e782a85d3899ec1cd09b_Out_0_Float, _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Out_3_Float, _Voronoi_643b106af3a65783a12e2e29f7d5bf08_Cells_4_Float);
float _Power_8fbb4fc95c43fa85a557eeba14ba0536_Out_2_Float;
Unity_Power_float(_Voronoi_643b106af3a65783a12e2e29f7d5bf08_Out_3_Float, float(6.37), _Power_8fbb4fc95c43fa85a557eeba14ba0536_Out_2_Float);
float4 _Multiply_0bc1fa627409228d97befdc2b6c7bc8e_Out_2_Vector4;
Unity_Multiply_float4_float4(_Property_6f505a52783e410ba93f48a53098d428_Out_0_Vector4, (_Power_8fbb4fc95c43fa85a557eeba14ba0536_Out_2_Float.xxxx), _Multiply_0bc1fa627409228d97befdc2b6c7bc8e_Out_2_Vector4);
float4 _Clamp_89a4342914bd4a889552ea096e238c47_Out_3_Vector4;
Unity_Clamp_float4(_Multiply_0bc1fa627409228d97befdc2b6c7bc8e_Out_2_Vector4, float4(0, 0, 0, 0), float4(1, 1, 1, 1), _Clamp_89a4342914bd4a889552ea096e238c47_Out_3_Vector4);
float2 _Twirl_94d8999b06dd05828372ad967f9f92b0_Out_4_Vector2;
Unity_Twirl_float(IN.uv0.xy, float2 (0.5, 0.5), float(2.77), float2 (0, 0.9), _Twirl_94d8999b06dd05828372ad967f9f92b0_Out_4_Vector2);
float _Property_ca45d9384f2c10849ae343dcf1a1a0ca_Out_0_Float = Vector1_3067A95E;
float _Multiply_25879efc1a342788bbf6716de383633c_Out_2_Float;
Unity_Multiply_float_float(IN.TimeParameters.x, _Property_ca45d9384f2c10849ae343dcf1a1a0ca_Out_0_Float, _Multiply_25879efc1a342788bbf6716de383633c_Out_2_Float);
float _Property_06992a081813058e914e60e75cc3632c_Out_0_Float = Vector1_832412A8;
float _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Out_3_Float;
float _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Cells_4_Float;
Unity_Voronoi_LegacySine_float(_Twirl_94d8999b06dd05828372ad967f9f92b0_Out_4_Vector2, _Multiply_25879efc1a342788bbf6716de383633c_Out_2_Float, _Property_06992a081813058e914e60e75cc3632c_Out_0_Float, _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Out_3_Float, _Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Cells_4_Float);
float _Power_709ff8d3522eff8aa8f7dd275eaa21f6_Out_2_Float;
Unity_Power_float(_Voronoi_5c3514d776c5e58d88ed72bfe17201b2_Out_3_Float, float(10.08), _Power_709ff8d3522eff8aa8f7dd275eaa21f6_Out_2_Float);
float4 _Property_b88c0a199d96491789488a85d34ec2e2_Out_0_Vector4 = _Color_Small_Noise;
float4 _Multiply_bd760fd69e6a938f90778a96d4a40b23_Out_2_Vector4;
Unity_Multiply_float4_float4((_Power_709ff8d3522eff8aa8f7dd275eaa21f6_Out_2_Float.xxxx), _Property_b88c0a199d96491789488a85d34ec2e2_Out_0_Vector4, _Multiply_bd760fd69e6a938f90778a96d4a40b23_Out_2_Vector4);
float4 _Clamp_d11eaf97a938ea87b061ca0f3369c51b_Out_3_Vector4;
Unity_Clamp_float4(_Multiply_bd760fd69e6a938f90778a96d4a40b23_Out_2_Vector4, float4(0, 0, 0, 0), float4(1, 1, 1, 1), _Clamp_d11eaf97a938ea87b061ca0f3369c51b_Out_3_Vector4);
float4 _Add_5c56eb92b361ce8396d260f92cdd97da_Out_2_Vector4;
Unity_Add_float4(_Clamp_89a4342914bd4a889552ea096e238c47_Out_3_Vector4, _Clamp_d11eaf97a938ea87b061ca0f3369c51b_Out_3_Vector4, _Add_5c56eb92b361ce8396d260f92cdd97da_Out_2_Vector4);
float4 _Add_f5d985425e6f8b8e9c42ca03bb1c768c_Out_2_Vector4;
Unity_Add_float4(_Multiply_929d0e10afdf118191dca672449de841_Out_2_Vector4, _Add_5c56eb92b361ce8396d260f92cdd97da_Out_2_Vector4, _Add_f5d985425e6f8b8e9c42ca03bb1c768c_Out_2_Vector4);
float4 _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4;
Unity_Add_float4(_SampleTexture2D_8947421d7150cc869ac2ca64bac07a8e_RGBA_0_Vector4, _Add_f5d985425e6f8b8e9c42ca03bb1c768c_Out_2_Vector4, _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4);
float4 _Multiply_e52f001f7bd7cc85b697cf4fd1a51d4f_Out_2_Vector4;
Unity_Multiply_float4_float4(Color_6c9e3069fc3b4e8e99792649df9fe6a1, _Add_8f30f6a9c3bbb98a8894cda7cd12bc20_Out_2_Vector4, _Multiply_e52f001f7bd7cc85b697cf4fd1a51d4f_Out_2_Vector4);
surface.BaseColor = (_Multiply_e52f001f7bd7cc85b697cf4fd1a51d4f_Out_2_Vector4.xyz);
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