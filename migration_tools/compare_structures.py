#!/usr/bin/env python3
"""
File structure comparison utility for migration from flat to jiraclean namespace.

This script analyzes differences between the parallel package structures and
reports on files that need to be migrated or merged.
"""

import os
import difflib
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# Configuration
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FLAT_ROOT = ROOT_DIR / "src"
JIRACLEAN_ROOT = ROOT_DIR / "src" / "jiraclean"

# Directories to exclude from comparison
EXCLUDE_DIRS = {
    "domain",
    "infrastructure",
    "__pycache__",
}

# File extensions to analyze
INCLUDE_EXTENSIONS = {
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".txt",
}


def calculate_file_hash(filepath: Path) -> str:
    """Calculate MD5 hash of a file."""
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def get_files(base_dir: Path, exclude_dirs: Optional[Set[str]] = None) -> Dict[str, Path]:
    """
    Get all files under base_dir, excluding specified directories.
    
    Returns a dictionary mapping relative path to absolute path.
    """
    if exclude_dirs is None:
        exclude_dirs = set()
    
    result = {}
    
    for root, dirs, files in os.walk(base_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        root_path = Path(root)
        for file in files:
            file_path = root_path / file
            if file_path.suffix in INCLUDE_EXTENSIONS:
                # Get path relative to base_dir
                rel_path = file_path.relative_to(base_dir)
                result[str(rel_path)] = file_path
    
    return result


def file_content_diff(file1: Path, file2: Path) -> float:
    """
    Compare file contents and return a similarity ratio (0.0 to 1.0).
    
    0.0 means completely different, 1.0 means identical.
    """
    try:
        with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
            content1 = f1.readlines()
            content2 = f2.readlines()
        
        matcher = difflib.SequenceMatcher(None, content1, content2)
        return matcher.ratio()
    except Exception as e:
        print(f"Error comparing {file1} and {file2}: {e}")
        return 0.0


def analyze_differences() -> Dict[str, List[Dict]]:
    """
    Analyze differences between flat and jiraclean structures.
    
    Returns a dictionary with categories of files and their details.
    """
    # Get files from both structures
    flat_files = get_files(FLAT_ROOT, EXCLUDE_DIRS)
    jiraclean_files = get_files(JIRACLEAN_ROOT)
    
    # Analysis results
    results = {
        "identical": [],       # Same content in both structures
        "similar": [],         # Similar but not identical content
        "flat_only": [],       # Only exists in flat structure
        "jiraclean_only": [],  # Only exists in jiraclean structure
    }
    
    # Check flat files against jiraclean structure
    for rel_path, flat_path in flat_files.items():
        # Skip any paths that are within the jiraclean directory
        if rel_path.startswith("jiraclean/"):
            continue
        
        # Look for potential match in jiraclean structure
        jiraclean_rel_path = rel_path
        jiraclean_path = jiraclean_files.get(jiraclean_rel_path)
        
        if jiraclean_path:
            # File exists in both structures, compare content
            flat_hash = calculate_file_hash(flat_path)
            jira_hash = calculate_file_hash(jiraclean_path)
            
            if flat_hash == jira_hash:
                results["identical"].append({
                    "flat_path": str(flat_path),
                    "jiraclean_path": str(jiraclean_path),
                    "rel_path": rel_path,
                    "status": "identical"
                })
            else:
                # Files have different content
                similarity = file_content_diff(flat_path, jiraclean_path)
                results["similar"].append({
                    "flat_path": str(flat_path),
                    "jiraclean_path": str(jiraclean_path),
                    "rel_path": rel_path,
                    "similarity": similarity,
                    "status": "similar"
                })
        else:
            # File only exists in flat structure
            results["flat_only"].append({
                "flat_path": str(flat_path),
                "rel_path": rel_path,
                "status": "flat_only"
            })
    
    # Identify files that only exist in jiraclean structure
    for rel_path, jiraclean_path in jiraclean_files.items():
        flat_path = flat_files.get(rel_path)
        if not flat_path:
            results["jiraclean_only"].append({
                "jiraclean_path": str(jiraclean_path),
                "rel_path": rel_path,
                "status": "jiraclean_only"
            })
    
    return results


def print_summary(results: Dict[str, List[Dict]]) -> None:
    """Print a summary of the analysis results."""
    print("\n=== STRUCTURE COMPARISON SUMMARY ===\n")
    
    print(f"Identical files: {len(results['identical'])}")
    print(f"Similar files: {len(results['similar'])}")
    print(f"Files only in flat structure: {len(results['flat_only'])}")
    print(f"Files only in jiraclean structure: {len(results['jiraclean_only'])}")
    
    print("\n=== FILES REQUIRING ATTENTION ===\n")
    
    if results["similar"]:
        print("\nFILES WITH DIFFERENCES (need to be merged):")
        for item in sorted(results["similar"], key=lambda x: x["similarity"]):
            print(f"  {item['rel_path']} (similarity: {item['similarity']:.2f})")
    
    if results["flat_only"]:
        print("\nFILES ONLY IN FLAT STRUCTURE (need to be migrated):")
        for item in sorted(results["flat_only"], key=lambda x: x["rel_path"]):
            print(f"  {item['rel_path']}")
    
    print("\n=== MIGRATION RECOMMENDATIONS ===\n")
    
    # Basic recommendations
    if results["similar"]:
        print("1. Review and merge the different versions of files, prioritizing by lowest similarity")
    
    if results["flat_only"]:
        print("2. Move unique files from flat structure to jiraclean namespace")
    
    if len(results["identical"]) > 0:
        print("3. Once functionality is verified, remove duplicate files from flat structure")


def generate_migration_report(results: Dict[str, List[Dict]]) -> str:
    """Generate a detailed migration report in Markdown format."""
    report = "# Migration Comparison Report\n\n"
    
    report += "## Summary\n\n"
    report += f"- Identical files: {len(results['identical'])}\n"
    report += f"- Similar files (need merging): {len(results['similar'])}\n"
    report += f"- Files only in flat structure (need migration): {len(results['flat_only'])}\n"
    report += f"- Files only in jiraclean structure: {len(results['jiraclean_only'])}\n\n"
    
    if results["similar"]:
        report += "## Files Needing Merge (Different Content)\n\n"
        report += "| File Path | Similarity | Flat Path | Jiraclean Path |\n"
        report += "|-----------|------------|-----------|----------------|\n"
        
        for item in sorted(results["similar"], key=lambda x: x["similarity"]):
            report += f"| {item['rel_path']} | {item['similarity']:.2f} | {item['flat_path']} | {item['jiraclean_path']} |\n"
        
        report += "\n"
    
    if results["flat_only"]:
        report += "## Files To Migrate (Flat Structure Only)\n\n"
        report += "| File Path | Current Location | Target Location |\n"
        report += "|-----------|------------------|----------------|\n"
        
        for item in sorted(results["flat_only"], key=lambda x: x["rel_path"]):
            target = f"src/jiraclean/{item['rel_path']}"
            report += f"| {item['rel_path']} | {item['flat_path']} | {target} |\n"
        
        report += "\n"
    
    if results["identical"]:
        report += "## Identical Files (Can Be Removed After Verification)\n\n"
        report += "| File Path | Flat Path | Jiraclean Path |\n"
        report += "|-----------|-----------|----------------|\n"
        
        for item in sorted(results["identical"], key=lambda x: x["rel_path"]):
            report += f"| {item['rel_path']} | {item['flat_path']} | {item['jiraclean_path']} |\n"
    
    report += "\n## Next Steps\n\n"
    report += "1. Start with merging similar files, beginning with those having lowest similarity score\n"
    report += "2. Migrate files that only exist in the flat structure to the jiraclean namespace\n"
    report += "3. Update imports in all files to use the jiraclean namespace\n"
    report += "4. After testing the consolidated structure, remove redundant files from the flat structure\n"
    
    return report


def main():
    """Main entry point."""
    print("Analyzing package structures...")
    results = analyze_differences()
    print_summary(results)
    
    # Generate and save migration report
    report = generate_migration_report(results)
    report_path = ROOT_DIR / "migration_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\nDetailed migration report saved to: {report_path}")


if __name__ == "__main__":
    main()
