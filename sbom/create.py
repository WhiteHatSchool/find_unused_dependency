import subprocess
import os
import json

def generate_sbom(project_path, output_file_path, format='cyclonedx-json'):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Run the syft command to generate SBOM in JSON format
    try:
        with open(output_file_path, 'w') as outfile:
            result = subprocess.run(['syft', project_path, '-o', format], check=True, capture_output=True, text=True)
            outfile.write(result.stdout)
        print(f'SBOM generated successfully at {output_file_path}')
            
    except subprocess.CalledProcessError as e:
        print(f'Error generating SBOM: {e}')
        print('Command output:', e.stdout)
        print('Command error output:', e.stderr)
    

def pretty_print_json(input_file_path, output_file_path):
    with open(input_file_path, 'r') as infile:
        data = json.load(infile)

    with open(output_file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

def create_sbom(project_dir):
    temp_output_file_path = './result/syft_sbom.json'
    final_output_file_path = './result/syft_sbom.json'
    
    # Generate the SBOM
    generate_sbom(project_dir, temp_output_file_path)

    # Pretty print the JSON file
    pretty_print_json(temp_output_file_path, final_output_file_path)

    # Optionally, remove the temporary file
    # os.remove(temp_output_file_path)
    