import subprocess
import json
import os
from create_movie import create_movie

def get_text(user_input):
    env = os.environ.copy()
    env["USER_INPUT"] = user_input
    result = subprocess.run(["modal", "run", "get_text.py"], capture_output=True, text=True, env=env)
    
    # Debug: print the full output
    print("Full output from get_text.py:", result.stdout)
    
    # Filter the JSON part from the output
    output_lines = result.stdout.splitlines()
    json_output = None
    for line in output_lines:
        try:
            json_output = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    if json_output is None:
        raise ValueError("No valid JSON output found.")
    return json_output

def extract_scenes(full_text):
    scenes = []
    scene_start_indices = [i for i, line in enumerate(full_text.split("\n")) if line.startswith("Scene")]
    for i in range(len(scene_start_indices)):
        start_index = scene_start_indices[i]
        end_index = scene_start_indices[i + 1] if i + 1 < len(scene_start_indices) else None
        scene_text = "\n".join(full_text.split("\n")[start_index:end_index]).strip()
        # Remove the "Scene X: " part
        scene_text = scene_text.split(':', 1)[1].strip() if ':' in scene_text else scene_text
        scenes.append(scene_text)
    return scenes

def parse_scene(scene):
    lines = scene.split("\n")
    parsed_lines = []
    for line in lines:
        if ':' in line:
            speaker, dialogue = line.split(':', 1)
            dialogue = dialogue.strip().strip('"')
            parsed_lines.append((speaker.strip(), dialogue))
    return parsed_lines

def generate_images(scenes):
    image_urls = []
    for i, scene in enumerate(scenes):
        previous_scenes = ' '.join(scenes[:i])
        prompt = f"Please generate this scene as a part of a larger story: {scene}. Here are the previous scenes of the story: {previous_scenes}."
        result = subprocess.run(
            ["python3", "generate_image.py", prompt],
            capture_output=True,
            text=True
        )
        image_url = result.stdout.strip()
        if image_url:  # Check if the URL is not empty
            image_urls.append(image_url)
    return image_urls

def assign_voices(parsed_scenes):
    voices = {}
    current_voice_index = 0
    available_voices = ['en', 'en-us', 'en-uk', 'en-au', 'en-ca']  # Example voices, you can add more

    for scene in parsed_scenes:
        for speaker, _ in scene:
            if speaker not in voices:
                voices[speaker] = available_voices[current_voice_index % len(available_voices)]
                current_voice_index += 1

    return voices

if __name__ == "__main__":
    user_input = (
        "Generate a storyboard for an advertisement on a pair of Super Green Alien Sneakers by Austin's Shoe Company. Break it down into scenes and describe each scene graphically in great detail. Give the list of scenes in the format (the following is an example) Scene N: [scene], Scene N+1: [scene]. Generate at least 5 Scenes. "
    )
    
    output = get_text(user_input)
    scenes = extract_scenes(output[0])
    
    image_urls = generate_images(scenes)
    
    for i, scene in enumerate(scenes):
        print(f"\nScene {i+1}: {scene}\nImage URL: {image_urls[i]}\n\n")

    # Save image URLs to JSON file
    with open("image_urls.json", "w") as file:
        json.dump(image_urls, file)

    # Create script based on scenes
    script_prompt = "I have a bunch of scenes: "
    for scene in scenes:
        script_prompt += scene
    script_prompt += "can you generate ONLY dialogue involving characters or a narrator (feel free to do whatever) for each scene and make it coherent throughout the whole story? Here are some examples of the format involving characters: Scene 1: Mom: 'How about we order from Marco’s Pizza tonight? They have the best pizzas in town!' Dad: 'I'm in! I’ve been craving their pepperoni pizza all day.' Jamie: 'Yes! And can we get the garlic knots too? They’re amazing.' And here is an example of a narration: Scene 1: Narrator: 'At Marco’s Pizza, we believe in the magic of fresh ingredients.' Scene 2: Narrator: Narrator: 'Every pizza starts with our hand-tossed dough, perfectly baked to a golden crisp. Do not include anything other than dialogue. And actually just do narrator only for now.'"
    
    # write the script for audio
    script_output = get_text(script_prompt)
    script_scenes = extract_scenes(script_output[0])
    
    # Format scenes
    parsed_scenes = [parse_scene(scene) for scene in script_scenes]
    
    # Speakers
    voices = assign_voices(parsed_scenes)
    
    # Narrations
    narrations = []
    for scene in parsed_scenes:
        narration = " ".join([dialogue for speaker, dialogue in scene])
        narrations.append(narration.strip())
    
    print("Voices assigned:", voices)
    print("Narrations generated:", narrations)

    for i, scene in enumerate(parsed_scenes):
        print(f"\n {scene}\n\n")
    
    # Create movie from the generated images with narration
    if image_urls:
        create_movie(image_urls, narrations, voices)
    else:
        print("No valid images to create a movie.")





# import subprocess
# import json
# import os
# from create_movie import create_movie

# def get_text(user_input):
#     env = os.environ.copy()
#     env["USER_INPUT"] = user_input
#     result = subprocess.run(["modal", "run", "get_text.py"], capture_output=True, text=True, env=env)
#     # Filter the JSON part from the output
#     output_lines = result.stdout.splitlines()
#     json_output = None
#     for line in output_lines:
#         try:
#             json_output = json.loads(line)
#             break
#         except json.JSONDecodeError:
#             continue
#     if json_output is None:
#         raise ValueError("No valid JSON output found.")
#     return json_output

# def extract_scenes(full_text):
#     scenes = []
#     scene_start_indices = [i for i, line in enumerate(full_text.split("\n")) if line.startswith("Scene")]
#     for i in range(len(scene_start_indices)):
#         start_index = scene_start_indices[i]
#         end_index = scene_start_indices[i + 1] if i + 1 < len(scene_start_indices) else None
#         scene_text = "\n".join(full_text.split("\n")[start_index:end_index]).strip()
#         # Remove the "Scene X: " part
#         scene_text = scene_text.split(':', 1)[1].strip() if ':' in scene_text else scene_text
#         scenes.append(scene_text)
#     return scenes

# def parse_scene(scene):
#     lines = scene.split("\n")
#     parsed_lines = []
#     for line in lines:
#         if ':' in line:
#             speaker, dialogue = line.split(':', 1)
#             dialogue = dialogue.strip().strip('"')
#             parsed_lines.append((speaker.strip(), dialogue))
#     return parsed_lines

# def generate_images(scenes):
#     image_urls = []
#     for i, scene in enumerate(scenes):
#         previous_scenes = ' '.join(scenes[:i])
#         prompt = f"Please generate this scene as a part of a larger story: {scene}. Here are the previous scenes of the story: {previous_scenes}."
#         result = subprocess.run(
#             ["python3", "generate_image.py", prompt],
#             capture_output=True,
#             text=True
#         )
#         image_url = result.stdout.strip()
#         if image_url:  # Check if the URL is not empty
#             image_urls.append(image_url)
#     return image_urls

# def assign_voices(parsed_scenes):
#     voices = {}
#     current_voice_index = 0
#     available_voices = ['en', 'en-us', 'en-uk', 'en-au', 'en-ca']  # Example voices, you can add more

#     for scene in parsed_scenes:
#         for speaker, _ in scene:
#             if speaker not in voices:
#                 voices[speaker] = available_voices[current_voice_index % len(available_voices)]
#                 current_voice_index += 1

#     return voices

# if __name__ == "__main__":
#     user_input = (
#         "Generate a storyboard for an advertisement on a pair of Super Green Alien Sneakers by Austin's Shoe Company. Break it down into scenes and describe each scene graphically in great detail. Give the list of scenes in the format (the following is an example) Scene N: [scene], Scene N+1: [scene]. Generate at least 5 Scenes. "
#     )
    
#     output = get_text(user_input)
#     scenes = extract_scenes(output[0])
    
#     image_urls = generate_images(scenes)
    
#     for i, scene in enumerate(scenes):
#         print(f"\nScene {i+1}: {scene}\nImage URL: {image_urls[i]}\n\n")

#     # Save image URLs to JSON file
#     with open("image_urls.json", "w") as file:
#         json.dump(image_urls, file)

#     # Create script based on scenes
#     script_prompt = "I have a bunch of scenes: "
#     for scene in scenes:
#         script_prompt += scene
#     script_prompt += "can you generate ONLY dialogue involving characters or a narrator (feel free to do whatever) for each scene and make it coherent throughout the whole story? Here are some examples of the format involving characters: Scene 1: Mom: 'How about we order from Marco’s Pizza tonight? They have the best pizzas in town!' Dad: 'I'm in! I’ve been craving their pepperoni pizza all day.' Jamie: 'Yes! And can we get the garlic knots too? They’re amazing.' And here is an example of a narration: Scene 1: Narrator: 'At Marco’s Pizza, we believe in the magic of fresh ingredients.' Scene 2: Narrator: Narrator: 'Every pizza starts with our hand-tossed dough, perfectly baked to a golden crisp. Do not include anything other than dialogue. And actually just do narrator only for now.'"
    
#     # write the script for audio
#     script_output = get_text(script_prompt)
#     script_scenes = extract_scenes(script_output[0])
    
#     # Format scenes
#     parsed_scenes = [parse_scene(scene) for scene in script_scenes]
    
#     # Speakers
#     voices = assign_voices(parsed_scenes)
    
#     # Narrations
#     narrations = []
#     for scene in parsed_scenes:
#         narration = " ".join([dialogue for speaker, dialogue in scene])
#         narrations.append(narration.strip())
    
#     print("Voices assigned:", voices)
#     print("Narrations generated:", narrations)

#     for i, scene in enumerate(parsed_scenes):
#         print(f"\n {scene}\n\n")
    
#     # Create movie from the generated images with narration
#     if image_urls:
#         create_movie(image_urls, narrations, voices)
#     else:
#         print("No valid images to create a movie.")
