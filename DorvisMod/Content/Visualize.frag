Pixel

fragment ViewColor

inputs
{
	float2 Uv;
	float4 VertexColor;
	texture Texture0;
}

outputs
{
	float4 Color;
}

fragmentCode

void ViewColor(inout Data data)
{
	data.Color = data.VertexColor * tex2D(Texture0, data.Uv);
	data.Color.a = 1.0;
}

fragment ViewDepth

inputs
{
	float2 Uv;
	float4 VertexColor;
	texture Texture0;
}

outputs
{
	float4 Color;
}

fragmentCode

void ViewDepth(inout Data data)
{
	float depth = -tex2D(Texture0, data.Uv).w;
	float adjusted = abs(cos(depth * 100)) * (1 - depth / 2);
	data.Color = float4(adjusted, adjusted, adjusted, 1);
	if (depth > 1.0)
		data.Color = float4(depth, 0, 0, 1);

}