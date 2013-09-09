Pixel

fragment PostCopy

inputs
{
	float2 Uv;
	texture Color0;
}

outputs
{
	float4 Color;
}

fragmentCode void PostCopy(inout Data data)
{
	data.Color = tex2D(Color0, data.Uv);
}

fragment PostCombine

inputs
{
	float2 Uv;
	texture Color0;
	texture Color1;
}

outputs
{
	float4 Color;
}

fragmentCode void PostCombine(inout Data data)
{
	float4 a = tex2D(Color0, data.Uv);
	float4 b = tex2D(Color1, data.Uv);
	data.Color = a + b;
}


fragment PostModulate

inputs
{
	float2 Uv;
	float4 ModulateColor;
	texture Color0;
}

outputs
{
	float4 Color;
}

fragmentCode void PostModulate(inout Data data)
{
	float4 a = tex2D(Color0, data.Uv);
	data.Color = a * data.ModulateColor;
}

fragment PostDownSample

inputs
{
	float2 Uv;
	float2 InvScreenDim;
	texture Color0;
}

outputs
{
	float4 Color;
}

fragmentCode

Constant float2 samplerOffsets[4] = 
ArrayStart(float2)
	float2(-1,-1), 
	float2(1,-1), 
	float2(1,1), 
	float2(-1,1)
ArrayEnd;

void PostDownSample(inout Data data)
{
	float4 average = float4(0,0,0,0);

	//Average 4x4 block from Color0
	for(int i=0;i<4;++i)
		average += tex2D(Color0, data.Uv + samplerOffsets[i] * data.InvScreenDim);
	average = average * 0.25f;
	data.Color = average;
}

fragment PostHighPass

inputs
{
	float BrightThreshold;
	float4 Color;
}

outputs
{
	float4 Color;
}

fragmentCode void PostHighPass(inout Data data)
{
	float4 average = data.Color;

	// Compute luminace using maxing
	float luminance = max(average.r, max(average.g, average.b));
	// Compute luminace constants
	//float luminance = dot( average.rgb, float3( 0.299f, 0.587f, 0.114f ) );

	// Bright pass
	if ( luminance < BrightThreshold )
		average = float4( 0.0f, 0.0f, 0.0f, 1.0f );
	
	data.Color = average;
}

