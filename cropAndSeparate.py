# We found out the preview grid is 3:4, but the image will always be cropped when uploaded to 4:5, even if you select original

import os
import math
from PIL import Image

def calculate_black_line_size(tile_width):
    """Calculate black line size as 1.5% of tile width"""
    return max(1, round(tile_width * 0.015))

def split_image(input_file, output_dir, aspect_ratio, black_lines=False):
    """Split image into tiles with exact aspect ratio handling 4:5 tiles containing 3:4 preview areas"""
    num_cols, num_rows = 3, 2
    target_ar = (3, 4)  # Seamless preview aspect ratio
    tile_ar = tuple(map(int, aspect_ratio.split(':')))  # Final tile aspect ratio
    
    with Image.open(input_file) as img:
        orig_w, orig_h = img.size
        
        # Calculate maximum grid size that satisfies both aspect ratios
        k = min(
            orig_w // (num_cols * tile_ar[0]),
            orig_h // (num_rows * tile_ar[1])
        )
        
        # Calculate final grid dimensions
        grid_w = num_cols * tile_ar[0] * k
        grid_h = num_rows * tile_ar[1] * k
        
        # Calculate preview area dimensions (3:4 ratio)
        preview_w = (target_ar[0] * grid_h * num_cols) // (target_ar[1] * num_rows)
        preview_h = grid_h
        
        # Center preview area in grid
        preview_left = (grid_w - preview_w) // 2
        preview_right = preview_left + preview_w
        
        # Apply black lines compensation if needed
        if black_lines:
            line_size = calculate_black_line_size(tile_ar[0] * k)
            grid_w += (num_cols - 1) * line_size
            grid_h += (num_rows - 1) * line_size
        
        # Center crop original image
        left = (orig_w - grid_w) // 2
        top = (orig_h - grid_h) // 2
        cropped = img.crop((left, top, left + grid_w, top + grid_h))
        
        os.makedirs(output_dir, exist_ok=True)
        output_files = []
        tile_number = num_cols * num_rows  # Start from 6
        
        for row in range(num_rows):
            for col in range(num_cols):
                # Calculate tile coordinates
                if black_lines:
                    x0 = col * (tile_ar[0]*k + line_size)
                    y0 = row * (tile_ar[1]*k + line_size)
                else:
                    x0 = col * tile_ar[0]*k
                    y0 = row * tile_ar[1]*k
                
                x1 = x0 + tile_ar[0]*k
                y1 = y0 + tile_ar[1]*k
                
                # Extract tile
                tile = cropped.crop((x0, y0, x1, y1))
                
                # Calculate preview area coordinates (3:4 ratio centered in 4:5 tile)
                preview_ratio = target_ar[0]/target_ar[1]
                tile_w, tile_h = tile.size
                
                if tile_w/tile_h > preview_ratio:
                    # Width-limited preview
                    preview_width = int(tile_h * preview_ratio)
                    preview_x0 = (tile_w - preview_width) // 2
                    preview_x1 = preview_x0 + preview_width
                    preview_area = (preview_x0, 0, preview_x1, tile_h)
                else:
                    # Height-limited preview
                    preview_height = int(tile_w / preview_ratio)
                    preview_y0 = (tile_h - preview_height) // 2
                    preview_y1 = preview_y0 + preview_height
                    preview_area = (0, preview_y0, tile_w, preview_y1)
                
                # Verify preview area matches grid coordinates
                grid_x = preview_left + col * (preview_w // num_cols)
                grid_y = row * (preview_h // num_rows)
                preview_tile = cropped.crop((
                    grid_x, grid_y,
                    grid_x + (preview_w // num_cols),
                    grid_y + (preview_h // num_rows)
                ))
                
                # Ensure preview area matches
                tile.paste(preview_tile.resize(
                    (preview_area[2] - preview_area[0],
                    preview_area[3] - preview_area[1])
                ), preview_area)

                
                # Save tile
                output_path = os.path.join(output_dir, f"{tile_number}.jpg")
                tile.save(output_path)
                output_files.append(output_path)
                tile_number -= 1

    return output_files

def split_image_with_black_lines_spacing(input_file, output_dir, aspect_ratio):
    return split_image(input_file, output_dir, aspect_ratio, black_lines=True)

def reconstruct_image(input_files, output_path, layout=(3,2), add_black_lines=False):
    """Reconstruct image from tiles with optional black lines"""
    images = [Image.open(f) for f in sorted(input_files, reverse=True)]
    tile_w, tile_h = images[0].size
    
    # Calculate line size based on first tile's width
    line_size = calculate_black_line_size(tile_w) if add_black_lines else 0
    
    # Create output canvas
    total_w = tile_w * layout[0] + line_size * (layout[0]-1)
    total_h = tile_h * layout[1] + line_size * (layout[1]-1)
    reconstructed = Image.new('RGB', (total_w, total_h), (0,0,0))
    
    # Paste tiles with optional lines
    for i, img in enumerate(images):
        row = i // layout[0]
        col = i % layout[0]
        x = col * (tile_w + line_size)
        y = row * (tile_h + line_size)
        reconstructed.paste(img, (x, y))
    
    reconstructed.save(output_path)
    return reconstructed

def main():
    input_file = "Me-4_01.jpg"
    output_dir = "separated_4x5"
    black_lines_dir = "separated_4x5_black_lines"
    
    print("Splitting image with 4:5 tiles containing 3:4 preview areas...")
    normal_tiles = split_image(input_file, output_dir, "4:5")
    
    print("\nSplitting with black lines compensation...")
    black_lines_tiles = split_image_with_black_lines_spacing(
        input_file, black_lines_dir, "4:5"
    )

    print("\nReconstructing preview grid...")
    preview_images = [Image.open(f) for f in normal_tiles]
    preview_w = sum(img.size[0] for img in preview_images[:3])
    preview_h = sum(img.size[1] for img in preview_images[:2])
    preview = Image.new('RGB', (preview_w, preview_h))
    
    for i, img in enumerate(preview_images):
        x = (i % 3) * img.size[0]
        y = (i // 3) * img.size[1]
        preview.paste(img, (x, y))
    
    preview.save("preview_grid.jpg")
    
    print("\nProcess complete. Outputs:")
    print(f"- 4:5 tiles: {output_dir}")
    print(f"- 4:5 tiles with black lines: {black_lines_dir}")
    print("- Preview grid: preview_grid.jpg")

if __name__ == "__main__":
    main()