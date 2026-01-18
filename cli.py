#!/usr/bin/env python3
"""
README Generator CLI
Automatically generate README.md files for your projects
"""
import click
import sys
from pathlib import Path

# Import our modules (we'll create these next)
try:
    from src.scanner import ProjectScanner
    from src.detector import TechDetector
    from src.template import TemplateGenerator
    from src.enhancer import AIEnhancer
except ImportError:
    # Fallback for when running directly
    sys.path.insert(0, str(Path(__file__).parent))
    from src.scanner import ProjectScanner
    from src.detector import TechDetector
    from src.template import TemplateGenerator
    from src.enhancer import AIEnhancer


@click.command()
@click.option('--path', '-p', default='.', help='Project directory to scan (default: current directory)')
@click.option('--output', '-o', default='README.md', help='Output file name (default: README.md)')
@click.option('--title', '-t', help='Project title (default: folder name)')
@click.option('--ai-enhance', '-a', is_flag=True, help='Use AI to enhance descriptions (requires API key)')
@click.option('--overwrite', '-w', is_flag=True, help='Overwrite existing README without asking')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed progress')
def generate(path, output, title, ai_enhance, overwrite, verbose):
    """
    Generate a professional README.md for your project
    
    Example usage:
        readme-gen --path ./my-project
        readme-gen --ai-enhance
        readme-gen --title "My Awesome Project" --output DOCS.md
    """
    
    # Resolve paths
    project_path = Path(path).resolve()
    output_path = project_path / output
    
    if verbose:
        click.echo(f"📂 Scanning project: {project_path}")
    
    # Check if project path exists
    if not project_path.exists():
        click.echo(f"❌ Error: Path '{path}' does not exist", err=True)
        sys.exit(1)
    
    # Check if README already exists
    if output_path.exists() and not overwrite:
        if not click.confirm(f"⚠️  {output} already exists. Overwrite?"):
            click.echo("❌ Aborted")
            sys.exit(0)
    
    try:
        # Step 1: Scan project
        if verbose:
            click.echo("🔍 Scanning files...")
        scanner = ProjectScanner(project_path)
        scan_results = scanner.scan()
        
        if verbose:
            click.echo(f"   Found {scan_results['file_count']} files in {scan_results['dir_count']} directories")
        
        # Step 2: Detect technologies
        if verbose:
            click.echo("🔎 Detecting technologies...")
        detector = TechDetector(scan_results)
        tech_info = detector.detect()
        
        if verbose:
            click.echo(f"   Detected: {', '.join(tech_info['languages'])}")
        
        # Step 3: Generate README template
        if verbose:
            click.echo("📝 Generating README...")
        
        project_title = title or project_path.name
        generator = TemplateGenerator(project_title, scan_results, tech_info)
        readme_content = generator.generate()
        
        # Step 4: AI enhancement (optional)
        if ai_enhance:
            if verbose:
                click.echo("🤖 Enhancing with AI...")
            enhancer = AIEnhancer()
            readme_content = enhancer.enhance(readme_content, scan_results, tech_info)
        
        # Step 5: Write to file
        output_path.write_text(readme_content)
        
        click.echo(f"✅ Successfully generated {output}")
        click.echo(f"📄 Location: {output_path}")
        
        if not ai_enhance:
            click.echo("\n💡 Tip: Use --ai-enhance for better descriptions (requires Claude API key)")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.command()
def version():
    """Show version information"""
    click.echo("README Generator v1.0.0")
    click.echo("Made with ❤️ by alxgraphy")


@click.group()
def cli():
    """README Generator - Automatically create professional README files"""
    pass


cli.add_command(generate)
cli.add_command(version)


if __name__ == '__main__':
    cli()