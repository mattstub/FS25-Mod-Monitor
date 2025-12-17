#!/usr/bin/env python3
"""
Mod Parser Unit Test
Tests modDesc.xml parsing and displays extracted data
Usage: python test_mod_parser.py <path_to_mod.zip>
"""

import sys
import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_mod(zip_path):
    """
    Parse a mod zip file and extract metadata
    Returns dict with mod information or None on error
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find modDesc.xml (case-insensitive)
            mod_desc_name = None
            for name in zip_ref.namelist():
                if name.lower().endswith('moddesc.xml'):
                    mod_desc_name = name
                    break
            
            if not mod_desc_name:
                return {
                    'error': 'modDesc.xml not found in zip',
                    'filename': Path(zip_path).name,
                    'files_in_zip': zip_ref.namelist()[:10]  # First 10 files
                }
            
            # Parse the XML
            with zip_ref.open(mod_desc_name) as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Extract all relevant information
                result = {
                    'filename': Path(zip_path).name,
                    'filesize': Path(zip_path).stat().st_size,
                    'modDesc_location': mod_desc_name,
                }
                
                # Title (try English first, then any language)
                title = root.find('.//title/en')
                if title is None:
                    title = root.find('.//title')
                result['title'] = title.text if title is not None else 'Unknown'
                
                # Version (from <version> element)
                version_elem = root.find('version')
                result['version'] = version_elem.text if version_elem is not None else 'Unknown'
                
                # Author
                author = root.find('.//author')
                result['author'] = author.text if author is not None else 'Unknown'
                
                # Description (try English first)
                desc = root.find('.//description/en')
                if desc is None:
                    desc = root.find('.//description')
                if desc is not None:
                    # Remove CDATA wrapper if present
                    desc_text = desc.text if desc.text else ''
                    result['description'] = desc_text.strip()[:200]  # First 200 chars
                else:
                    result['description'] = None
                
                # Additional metadata (for debugging)
                result['debug_info'] = {
                    'descVersion': root.get('descVersion', 'Not set'),
                    'iconFilename': root.find('iconFilename').text if root.find('iconFilename') is not None else None,
                    'multiplayer_supported': root.find('.//multiplayer').get('supported', 'unknown') if root.find('.//multiplayer') is not None else None,
                }
                
                # Count store items if present
                store_items = root.findall('.//storeItem')
                result['debug_info']['store_items_count'] = len(store_items)
                
                return result
    
    except zipfile.BadZipFile:
        return {'error': 'Invalid zip file', 'filename': Path(zip_path).name}
    except ET.ParseError as e:
        return {'error': f'XML parsing error: {e}', 'filename': Path(zip_path).name}
    except Exception as e:
        return {'error': f'Unexpected error: {e}', 'filename': Path(zip_path).name}

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def print_result(result):
    """Print the result in a formatted way"""
    print("\n" + "=" * 60)
    print("MOD PARSER TEST RESULT")
    print("=" * 60)
    
    if 'error' in result:
        print(f"\n❌ ERROR: {result['error']}")
        print(f"   File: {result['filename']}")
        if 'files_in_zip' in result:
            print(f"\n   Files in zip (first 10):")
            for f in result['files_in_zip']:
                print(f"     - {f}")
        return
    
    print(f"\n📦 Filename: {result['filename']}")
    print(f"📏 File Size: {format_size(result['filesize'])}")
    print(f"📄 modDesc.xml Location: {result['modDesc_location']}")
    
    print("\n" + "-" * 60)
    print("EXTRACTED METADATA (What Discord will show)")
    print("-" * 60)
    
    print(f"\n✅ Title: {result['title']}")
    print(f"✅ Version: {result['version']}")
    print(f"✅ Author: {result['author']}")
    
    if result.get('description'):
        print(f"\n📝 Description: {result['description']}")
    
    print("\n" + "-" * 60)
    print("DEBUG INFORMATION")
    print("-" * 60)
    
    debug = result.get('debug_info', {})
    print(f"\n🔍 descVersion (XML schema): {debug.get('descVersion', 'N/A')}")
    print(f"   Note: This is the FS25 mod format version, NOT the mod version")
    print(f"🔍 Icon File: {debug.get('iconFilename', 'N/A')}")
    print(f"🔍 Multiplayer: {debug.get('multiplayer_supported', 'N/A')}")
    print(f"🔍 Store Items: {debug.get('store_items_count', 0)}")
    
    print("\n" + "=" * 60)
    print("JSON OUTPUT")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n")

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_mod_parser.py <path_to_mod.zip>")
        print("\nExample:")
        print("  python test_mod_parser.py /path/to/FS25_ModName.zip")
        print("  python test_mod_parser.py ./mods/*.zip")
        sys.exit(1)
    
    mod_paths = sys.argv[1:]
    
    for mod_path in mod_paths:
        if not Path(mod_path).exists():
            print(f"❌ File not found: {mod_path}")
            continue
        
        result = parse_mod(mod_path)
        print_result(result)
        
        # Validation checks
        if 'error' not in result:
            print("=" * 60)
            print("VALIDATION CHECKS")
            print("=" * 60)
            
            checks = []
            
            if result['title'] != 'Unknown':
                checks.append("✅ Title extracted successfully")
            else:
                checks.append("⚠️  Title is 'Unknown' - check modDesc.xml structure")
            
            if result['version'] != 'Unknown':
                checks.append("✅ Version extracted successfully")
            else:
                checks.append("⚠️  Version is 'Unknown' - check if <version> element exists")
            
            if result['author'] != 'Unknown':
                checks.append("✅ Author extracted successfully")
            else:
                checks.append("⚠️  Author is 'Unknown' - check if <author> element exists")
            
            # Check version isn't descVersion
            debug = result.get('debug_info', {})
            if result['version'] == debug.get('descVersion'):
                checks.append("❌ WARNING: Version matches descVersion - likely parsing bug!")
            else:
                checks.append("✅ Version is different from descVersion (correct)")
            
            for check in checks:
                print(f"  {check}")
            
            print("\n")

if __name__ == "__main__":
    main()
