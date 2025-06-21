from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Optional, Dict, Union

class MLProjectCreator:
    """Machine Learning Project Structure Generator"""
    
    def __init__(self, folders: Optional[Union[List[str], Dict[str, any]]] = None) -> None:
        """
        Initialize project creator
        
        Args:
            folders: Folder structure configuration
                - List[str]: Simple folder list
                - Dict: Nested folder structure with subdirectories
        """
        # Default subfolder structure (with subdirectories)
        default_structure: Dict[str, List[str]] = {
            "data": ["raw", "output", "processed"],
            "models": ["checkpoints"],
            "utils": [],
            "logs": [],
            "configs": [],
            "notebooks": []
        }
        
        if folders is None:
            self.structure = default_structure
        elif isinstance(folders, list):
            # If list is passed, convert to simple dictionary structure
            self.structure = {folder: [] for folder in folders}
        else:
            self.structure = folders
    
    def _create_directory_recursive(self, base_path: Path, structure: Dict[str, List[str]]) -> None:
        """
        Recursively create directory structure
        
        Args:
            base_path (Path): Base path
            structure (Dict): Directory structure dictionary
        """
        for folder_name, sub_folders in structure.items():
            folder_path: Path = base_path / folder_name
            folder_path.mkdir(exist_ok=True)
            # print(f"Created directory: {folder_path.relative_to(Path.cwd())}")
            
            # Create subdirectories
            for sub_folder in sub_folders:
                sub_path: Path = folder_path / sub_folder
                sub_path.mkdir(exist_ok=True)
                # print(f"  Created subdirectory: {sub_path.relative_to(Path.cwd())}")
    
    def _print_directory_tree(self, path: Path, prefix: str = "", is_last: bool = True) -> None:
        """
        Print directory tree structure
        
        Args:
            path (Path): Directory path
            prefix (str): Prefix for tree display
            is_last (bool): Whether this is the last item at current level
        """
        if path.is_dir():
            # Print current directory
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{path.name}/")
            
            # Get subdirectories and files
            items = sorted([item for item in path.iterdir()])
            dirs = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            # Print subdirectories first
            for i, subdir in enumerate(dirs):
                is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                new_prefix = prefix + ("    " if is_last else "│   ")
                self._print_directory_tree(subdir, new_prefix, is_last_dir)
            
            # Print files
            for i, file in enumerate(files):
                is_last_file = (i == len(files) - 1)
                connector = "└── " if is_last_file else "├── "
                new_prefix = prefix + ("    " if is_last else "│   ")
                print(f"{new_prefix}{connector}{file.name}")
    
    def print_project_structure(self, project_root: Path) -> None:
        """
        Print the entire project structure
        
        Args:
            project_root (Path): Project root directory path
        """
        
        print(f"\n✅️ Created ML project successfully")
        print(f"\n📁 Project Structure:")
        print("=" * 50)
        print(f"{project_root.name}/")
        
        # Get all items in project root
        items = sorted([item for item in project_root.iterdir()])
        
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            self._print_directory_tree(item, "", is_last)
        
        print("=" * 50)
    
    def create_project(self, project_name: str) -> Path:
        """
        Create machine learning project structure
        
        Args:
            project_name (str): Project name
            
        Returns:
            Path: Created project root directory path
            
        Raises:
            ValueError: When project name is empty
            OSError: When unable to create directory
        """
        if not project_name.strip():
            raise ValueError("Project name cannot be empty")
        
        # Generate project folder name with timestamp
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_project_name: str = f"{project_name}_{timestamp}"
        
        # Create project root directory
        project_root: Path = Path.cwd() / full_project_name
        
        try:
            project_root.mkdir(exist_ok=True)
            # print(f"Created main project folder: {project_root}")
            
            # Create directory structure
            self._create_directory_recursive(project_root, self.structure)
            
            # print(f"Project creation completed: {project_root}")
            
            # Print project structure
            self.print_project_structure(project_root)
            
            return project_root
            
        except OSError as e:
            print(f"Error occurred while creating project: {e}")
            raise

def parse_folders_with_colon(folder_specs: List[str]) -> Dict[str, List[str]]:
    """
    Parse folder specifications with colon syntax
    
    Args:
        folder_specs: List of folder specifications, supporting formats:
            - "folder_name" : Simple folder
            - "folder_name:sub1,sub2,sub3" : Folder with subdirectories
    
    Returns:
        Dict: Parsed directory structure
    """
    result = {}
    
    for spec in folder_specs:
        if ':' in spec:
            folder_name, sub_spec = spec.split(':', 1)
            sub_folders = [s.strip() for s in sub_spec.split(',') if s.strip()]
            result[folder_name] = sub_folders
        else:
            # Simple folder
            result[spec] = []
    
    return result

def main() -> None:
    """Main function for command line execution"""
    parser = argparse.ArgumentParser(
        description='Machine Learning Project Structure Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default structure
  python %(prog)s my_project
  
  # Simple folders
  python %(prog)s my_project --folders data models scripts output
  
  # Folders with subdirectories (colon syntax)
  python %(prog)s my_project --folders "data:raw,processed,external" "models:trained,checkpoints" scripts
        """
    )
    
    parser.add_argument(
        'project_name', 
        type=str,
        help='Project name'
    )
    
    parser.add_argument(
        '--folders', 
        '-f',
        type=str,
        nargs='*',
        help='''Custom folder list, supporting colon syntax:
        Simple folder: folder_name
        Folder with subdirectories: "folder_name:sub1,sub2,sub3"'''
    )
    
    args = parser.parse_args()
    
    try:
        if args.folders:
            # Parse folders with colon syntax
            structure = parse_folders_with_colon(args.folders)
            creator = MLProjectCreator(folders=structure)
        else:
            # Use default structure
            creator = MLProjectCreator()
        
        creator.create_project(args.project_name)
        
    except ValueError as e:
        print(f"Input error: {e}")
        return
    except OSError as e:
        print(f"File system error: {e}")
        return
    except Exception as e:
        print(f"Unknown error: {e}")
        return

if __name__ == "__main__":
    main()

"""
# Use default structure
creator = MLProjectCreator()
creator.create_project("my_project")

# Custom nested structure
custom_structure = {
    "data": ["raw", "processed", "cleaned"],
    "models": ["experiments", "production"],
    "code": [],
    "results": ["plots", "reports"]
}
creator = MLProjectCreator(folders=custom_structure)
creator.create_project("custom_project")

# Simple structure
simple_folders = ["data", "models", "scripts", "output"]
creator = MLProjectCreator(folders=simple_folders)
creator.create_project("simple_project")


# Use default structure
python create_ml_project.py my_project

# Simple folders
python create_ml_project.py my_project --folders data models scripts output

# Folders with subdirectories (colon syntax)
python create_ml_project.py my_project --folders "data:raw,processed,external" "models:trained,checkpoints" scripts

# Complex example
python create_ml_project.py my_project --folders "data:input,output,temp" "models:saved,experiments" "results:plots,reports,metrics" logs

"""
