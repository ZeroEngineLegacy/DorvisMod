Pixel

////////////////////StoreDepth//////////////////////

fragment StoreDepth

inputs
{
	float3 PixelPosition;
	float FarDistance;
}

outputs
{
	float4 Color;
}

fragmentCode void StoreDepth(inout Data data)
{
	//Pixel position is in view space
	//float linearDepth = length(data.PixelPosition);
	float linearDepth = -data.PixelPosition.z / data.FarDistance;
	
	//Store depth into output
	data.Color = float4(linearDepth, 1, 1, 1);
}

/////////////////////////////////////////////

fragment BasicShadow

inputs
{
	float4x4 ShadowProjection;
	float4x4 ShadowView;
	float ShadowFarDistance;	
	texture ShadowMap;
}

outputs
{
	float LightIntensity;
}

fragmentCode void BasicShadow(inout Data data)
{
	//Project the pixel into the shadow space
	float4 positionInShadow = mul(ShadowProjection, float4(data.PixelPosition, 1) );
	float3 positionInView = mul(ShadowView, float4(data.PixelPosition, 1) ).xyz;
		
	//NDC to UV
	float2 shadowTex = 0.5 * (positionInShadow.xy / positionInShadow.w ) + float2( 0.5, 0.5 );
	
	//Read shadow map
	float4 shadowMap = tex2D(ShadowMap, shadowTex);
	float shadowDepth = shadowMap.r * data.ShadowFarDistance;	
	float depth = -positionInView.z;

	if (depth - 0.1 > shadowDepth)
		data.LightColor = data.ShadowColor;
}

fragment EsmShadow

inputs
{
	float4x4 ShadowProjection;
	float4x4 ShadowView;
	texture ShadowMap;
	float ShadowFarDistance;
	float4 ShadowColor;
}

outputs
{
	float LightIntensity;
}

fragmentCode 

float cOverDarkeningFactor = 1.0;
float cLightShadowBias = 0.01;
void EsmShadow(inout Data data)
{
	//Project the pixel into the shadow space
	float4 positionInShadow = mul(ShadowProjection, float4(data.PixelPosition, 1) );	
	float3 positionInView = mul(ShadowView, float4(data.PixelPosition, 1) ).xyz;
	
	//NDC to UV
	float2 shadowTex = 0.5 * (positionInShadow.xy / positionInShadow.w ) + float2( 0.5, 0.5 );
	
	//Read shadow map
	float4 shadowMap = tex2D(ShadowMap, shadowTex);
	float shadowDepth = shadowMap.r * data.ShadowFarDistance;
	
	float depth = -positionInView.z;
	float occluder = shadowDepth;
	float receiver = depth - cLightShadowBias;

	float shadowFactor = saturate(exp(cOverDarkeningFactor * ( occluder - receiver )));
	data.LightColor = lerp(data.ShadowColor, data.LightColor, shadowFactor);
}


