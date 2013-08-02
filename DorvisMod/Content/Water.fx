//Water2

float4x4 WorldViewProjection: WorldViewProjection;
float4x4 World: World;
float4x4 View: View;
float4x4 WorldView: WorldView;

float FarPlane = 50;

float Time;

float2 Tiling0 = float2(1, 1);
float2 Dir0 = float2(0.01, 0.01);

float2 Tiling1 = float2(0.4, 0.45);
float2 Dir1 = float2(-0.01, -0.01);

float2 Tiling2 = float2(0.1, 0.1);
float2 Dir2 = float2(0.005,0.005);

float3 EyePos = float3(0,0,0);

samplerCUBE Environment;

sampler2D Normals;

sampler2D Scene;

sampler2D DepthScene;


struct VS_INPUT
{
    float3 Position : POSITION;
    float2 Tex0 : TEXCOORD0;
    float3 Normal : NORMAL;
    float3 Tangent : TANGENT;
    float3 Binormal : BINORMAL;
};

struct VS_OUTPUT
{
    float4 Position : POSITION;
    float2 Tex0  : TEXCOORD0;
    float3 ViewPos : TEXCOORD1;
    float3 WorldPos : TEXCOORD5;
    float3 Normal : TEXCOORD2;
    float3 Tangent : TEXCOORD3;
    float4 Screen : TEXCOORD4;
};

const float scale = 100;

VS_OUTPUT VertexShader0( VS_INPUT In )
{
    VS_OUTPUT Out;
    float3 pos = In.Position * float3(scale,1,scale);
    Out.Position = mul(WorldViewProjection, float4(pos, 1) );
    Out.Normal = mul(World, float4(In.Normal,0)).xyz;
    Out.ViewPos = mul(WorldView, float4(pos, 1) ).xyz;
    Out.WorldPos = mul(World, float4(pos, 1) ).xyz;
    //Out.Binormal = mul(World, float4(In.Binormal,0)).xyz;
    Out.Tangent = mul(World, float4(In.Tangent, 0)).xyz;
    Out.Screen = Out.Position;
    Out.Tex0 = In.Tex0;
    return Out;
}

float FresnelBias = 0.2;
float FresnelExp = 1.76;
float ReflectionStr = 1.0;
float RefractiveIndex = 1.0;


float ShoreFadeDis = 0.3;

const float NormalRefractScalar = 0.1;

const float4 WaterDeepColor = float4(0.1,0.2,0.2,1);
	

float3 GetViewPosition(float3 viewPos, float4 sample)
{
    float3 worldView = viewPos;
	float3 viewDirection = float3(worldView.xy * (FarPlane / worldView.z), FarPlane);
	return sample.a * viewDirection;
}

float4 PixelShader0( VS_OUTPUT In ) : COLOR
{
   
    float3 Nn = normalize(In.Normal);
    float3 Tn = normalize(In.Tangent);
    float3 Bn = cross(Nn, Tn);

    float2 screenTex = 0.5 * (In.Screen.xy / In.Screen.w ) + float2( 0.5, 0.5 );


    float3 myViewPos = In.ViewPos;
	float3 otherViewPos = GetViewPosition(myViewPos, tex2D(DepthScene, screenTex));

    // Compute normal by averaging several normal map samples
    float2 baseTex = In.Tex0 * scale;
    float t = 0.01;
    float scale = 0.1;
    float4 normal1 = tex2D(Normals, baseTex * Tiling0 * scale + Dir0 * Time )*2.0-1.0;
    float4 normal2 = tex2D(Normals, baseTex * Tiling1 * scale + Dir1 * Time )*2.0-1.0;
    float4 normal3 = tex2D(Normals, baseTex * Tiling2 * scale + Dir2 * Time )*2.0-1.0;
    float normalScale = 0.5;
    float3 bump = normalScale * normalize(normal1.xyz + normal2.xyz + normal3.xyz);
    float3 normal = normalize( (Nn + bump.y*Tn + bump.x*Bn) );
    

    float3 toEye = normalize(EyePos - In.WorldPos);
    float3 reflectDir = reflect(-toEye, normal);
  
  
    float4 reflectColor  = texCUBE(Environment, reflectDir);
    float3 refactDir = refract(-toEye, normal, RefractiveIndex);  
        
    
    float2 refractOffsetUv = screenTex + normal.xz * NormalRefractScalar;
    
   	float3 samplePos = GetViewPosition(myViewPos, tex2D(DepthScene, refractOffsetUv)); 

    //If the sampled point is closer to the eye than the water
    //geometry reset the refractOffsetUv
    if(samplePos.z + 1 > myViewPos.z)
    {
        refractOffsetUv = screenTex;
        samplePos = otherViewPos;
        //return float4(1,1,1,0);
    }
    
    float waterDepth = abs(samplePos.z - myViewPos.z);
    
    float facing = saturate(dot(toEye, normal)); 
    float fres = ReflectionStr*(FresnelBias+(1.0-FresnelBias)*pow(facing, FresnelExp));
    
    float4 refractColor = tex2D(Scene, refractOffsetUv);

    float colorDecay = min(1.0, exp(-waterDepth/35.0) );

  	float4 finalColor = lerp(WaterDeepColor, refractColor, colorDecay);  	
    finalColor = (finalColor * fres + reflectColor * (1-fres)) * 0.6;
    
    float edgeDecay = min(1.0, exp(-waterDepth/5.0));
    return lerp(finalColor, refractColor, edgeDecay); 

}

technique Main
{
    pass
    {
        FragmentProgram = compile latest PixelShader0();
        VertexProgram = compile latest VertexShader0();
    }
}
