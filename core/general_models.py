

from .node_registry import register_node
from .base_node import BaseNode, text_input, slider, combo, handle, text_area, toggle

@register_node(
    name="ClipEncoder",
    description="CLIP Encoder - Encodes text into vector embeddings",
    category="general_models",
    icon="🔤"
)
class ClipEncoderNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        text: str = text_area(default="", description="Text to encode")
        clip_model: str = handle(description="CLIP Model", color_type="clip")
    
    class Outputs(BaseNode.Outputs):
        embedding: list
    
    def __call__(self, text: str = "", clip_model: str = "") -> dict:
        
        return {"embedding": [ord(c) for c in text[:10]]}

@register_node(
    name="VAEDecoder",
    description="VAE Decoder - Decodes latent space into images",
    category="general_models",
    icon="🖼️"
)
class VAEDecoderNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        latent: list = handle(description="Latent space", color_type="latent")
    
    class Outputs(BaseNode.Outputs):
        image: str
    
    def __call__(self, latent: list = []) -> dict:
        
        import json
        latent = json.loads(latent) if isinstance(latent, str) else latent
        return {"image": "decoded_image"}

@register_node(
    name="ImageProcessor",
    description="Image Processor - Processes and manipulates images",
    category="general_models",
    icon="🎨"
)
class ImageProcessorNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        image: str = handle(description="Image", color_type="image")
        filter: str = combo(default="none", description="Filter", options=["none", "grayscale", "sepia", "blur"])
    
    class Outputs(BaseNode.Outputs):
        processed_image: str
    
    def __call__(self, image: str = "", filter: str = "none") -> dict:
        
        return {"processed_image": f"{filter}_{image}"}

@register_node(
    name="LatentGenerator",
    description="Latent Generator - Generates latent space representations",
    category="general_models",
    icon="🌌"
)
class LatentGeneratorNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        seed: int = slider(default=42, description="Random seed", min=0, max=9999999999, step=1)
        dimensions: dict = text_input(default='{"width": 64, "height": 64}', description="Dimensions")
    
    class Outputs(BaseNode.Outputs):
        latent: list
    
    def __call__(self, seed: int = 42, dimensions: dict = {"width": 64, "height": 64}) -> dict:
        
        import json
        dimensions = json.loads(dimensions) if isinstance(dimensions, str) else dimensions
        return {"latent": [seed] * 10}
