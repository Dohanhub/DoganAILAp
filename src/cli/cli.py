#!/usr/bin/env python3
"""
CLI management tool for DoganAI-Compliance-Kit
"""
import typer
import sys
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.compliance import evaluate, get_available_mappings
from engine.validators import validate_directory, generate_validation_report
from engine.settings import settings
from engine.database import get_db_service

app = typer.Typer(help="DoganAI Compliance Kit Management CLI")
console = Console()

@app.command()
def validate(
    component: str = typer.Argument(..., help="Component to validate: policies, vendors, mappings, or all"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, or report"),
    save_report: Optional[str] = typer.Option(None, "--save", "-s", help="Save report to file")
):
    """Validate configuration files"""
    
    base_dir = Path(__file__).parent.parent
    valid_components = ["policies", "vendors", "mappings", "all"]
    
    if component not in valid_components:
        console.print(f"[red]Error:[/red] Invalid component. Must be one of: {', '.join(valid_components)}")
        raise typer.Exit(1)
    
    console.print(f"[blue]Validating {component}...[/blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        if component == "all":
            components_to_check = ["policies", "vendors", "mappings"]
        else:
            components_to_check = [component]
        
        all_results = {}
        
        for comp in components_to_check:
            task = progress.add_task(f"Validating {comp}...", total=None)
            
            comp_dir = base_dir / comp
            if comp_dir.exists():
                file_type = comp.rstrip('s')  # Remove trailing 's'
                results = validate_directory(comp_dir, file_type)
                all_results[comp] = results
            else:
                console.print(f"[yellow]Warning:[/yellow] Directory {comp_dir} does not exist")
                all_results[comp] = {}
            
            progress.remove_task(task)
    
    # Display results
    if output_format == "json":
        # Convert results to JSON-serializable format
        json_results = {}
        for comp, results in all_results.items():
            json_results[comp] = {}
            for filename, result in results.items():
                json_results[comp][filename] = {
                    "is_valid": result.is_valid,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
        
        output = json.dumps(json_results, indent=2)
        console.print(output)
        
        if save_report:
            with open(save_report, 'w') as f:
                f.write(output)
            console.print(f"[green]Report saved to {save_report}[/green]")
    
    elif output_format == "report":
        for comp, results in all_results.items():
            if results:
                report = generate_validation_report(results)
                console.print(f"\n[bold]{comp.upper()} VALIDATION REPORT[/bold]")
                console.print(report)
                
                if save_report:
                    report_file = f"{save_report}_{comp}.txt" if len(all_results) > 1 else save_report
                    with open(report_file, 'w') as f:
                        f.write(report)
                    console.print(f"[green]Report saved to {report_file}[/green]")
    
    else:  # table format
        for comp, results in all_results.items():
            if not results:
                continue
                
            table = Table(title=f"{comp.capitalize()} Validation Results")
            table.add_column("File", style="cyan")
            table.add_column("Status", justify="center")
            table.add_column("Errors", justify="center")
            table.add_column("Warnings", justify="center")
            
            for filename, result in results.items():
                status = "[green]? Valid[/green]" if result.is_valid else "[red]? Invalid[/red]"
                error_count = str(len(result.errors))
                warning_count = str(len(result.warnings))
                
                table.add_row(filename, status, error_count, warning_count)
            
            console.print(table)
            console.print()

@app.command()
def evaluate_mapping(
    mapping_name: str = typer.Argument(..., help="Name of the mapping to evaluate"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
    save_result: Optional[str] = typer.Option(None, "--save", "-s", help="Save result to file")
):
    """Evaluate a compliance mapping"""
    
    console.print(f"[blue]Evaluating mapping: {mapping_name}[/blue]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running evaluation...", total=None)
            
            result = evaluate(mapping_name)
            progress.remove_task(task)
        
        if output_format == "json":
            output = json.dumps(result, indent=2, ensure_ascii=False)
            console.print(output)
            
            if save_result:
                with open(save_result, 'w', encoding='utf-8') as f:
                    f.write(output)
                console.print(f"[green]Result saved to {save_result}[/green]")
        
        else:  # table format
            # Status panel
            status_color = {
                "COMPLIANT": "green",
                "PARTIAL": "yellow", 
                "GAPS": "red"
            }.get(result['status'], "white")
            
            status_panel = Panel(
                f"[bold {status_color}]{result['status']}[/bold {status_color}]",
                title="Compliance Status",
                border_style=status_color
            )
            console.print(status_panel)
            
            # Summary table
            summary_table = Table(title="Evaluation Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", justify="right")
            
            summary_table.add_row("Mapping", result['mapping'])
            summary_table.add_row("Policy", result['policy'])
            summary_table.add_row("Total Controls", str(len(result['required'])))
            summary_table.add_row("Compliant Controls", str(len(result['provided'])))
            summary_table.add_row("Missing Controls", str(len(result['missing'])))
            summary_table.add_row("Vendors", str(len(result['vendors'])))
            
            console.print(summary_table)
            
            # Vendors table
            if result['vendors']:
                vendors_table = Table(title="Vendors")
                vendors_table.add_column("Vendor", style="cyan")
                vendors_table.add_column("Solution")
                
                for vendor in result['vendors']:
                    vendors_table.add_row(
                        vendor.get('vendor', 'Unknown'),
                        vendor.get('solution', 'Unknown')
                    )
                
                console.print(vendors_table)
            
            # Missing controls
            if result['missing']:
                console.print(f"\n[red]Missing Controls ({len(result['missing'])}):[/red]")
                for control in result['missing']:
                    console.print(f"  � {control}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def list_mappings():
    """List all available mappings"""
    
    try:
        mappings = get_available_mappings()
        
        if not mappings:
            console.print("[yellow]No mappings found[/yellow]")
            return
        
        table = Table(title=f"Available Mappings ({len(mappings)})")
        table.add_column("Mapping Name", style="cyan")
        table.add_column("File", style="dim")
        
        for mapping in sorted(mappings):
            table.add_row(mapping, f"{mapping}.yaml")
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def check_health():
    """Run health checks"""
    
    console.print("[blue]Running health checks...[/blue]")
    
    try:
        from engine.health import get_health_checker
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running health checks...", total=None)
            
            health_checker = get_health_checker()
            result = health_checker.run_all_checks()
            
            progress.remove_task(task)
        
        # Overall status
        status_color = {
            "healthy": "green",
            "degraded": "yellow",
            "unhealthy": "red"
        }.get(result['status'], "white")
        
        overall_panel = Panel(
            f"[bold {status_color}]{result['status'].upper()}[/bold {status_color}]",
            title="Overall Health Status",
            border_style=status_color
        )
        console.print(overall_panel)
        
        # Summary
        summary = result.get('summary', {})
        console.print(f"Total Checks: {summary.get('total_checks', 0)}")
        console.print(f"Passed: [green]{summary.get('passed', 0)}[/green]")
        console.print(f"Warnings: [yellow]{summary.get('warnings', 0)}[/yellow]")
        console.print(f"Failed: [red]{summary.get('failed', 0)}[/red]")
        console.print(f"Duration: {result.get('duration_ms', 0):.2f}ms")
        
        # Individual checks
        checks_table = Table(title="Individual Checks")
        checks_table.add_column("Check", style="cyan")
        checks_table.add_column("Status", justify="center")
        checks_table.add_column("Message")
        
        for check_name, check_result in result.get('checks', {}).items():
            status = check_result.get('status', 'unknown')
            status_display = {
                'healthy': '[green]? Healthy[/green]',
                'warning': '[yellow]?? Warning[/yellow]',
                'error': '[red]? Error[/red]'
            }.get(status, f'[dim]{status}[/dim]')
            
            message = check_result.get('message', 'No message')
            checks_table.add_row(check_name, status_display, message)
        
        console.print(checks_table)
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def init_db():
    """Initialize the database"""
    
    console.print("[blue]Initializing database...[/blue]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Setting up database...", total=None)
            
            db_service = get_db_service()
            db_service.initialize()
            
            progress.remove_task(task)
        
        console.print("[green]? Database initialized successfully[/green]")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def config(
    show_sensitive: bool = typer.Option(False, "--show-sensitive", help="Show sensitive configuration values"),
    save_to: Optional[str] = typer.Option(None, "--save", "-s", help="Save configuration to file")
):
    """Show current configuration"""
    
    config_dict = settings.to_dict()
    
    if not show_sensitive:
        # Hide sensitive values
        sensitive_keys = ['password', 'secret', 'key', 'token']
        for key, value in config_dict.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                config_dict[key] = "***HIDDEN***"
    
    if save_to:
        with open(save_to, 'w') as f:
            json.dump(config_dict, f, indent=2)
        console.print(f"[green]Configuration saved to {save_to}[/green]")
    else:
        # Display as table
        table = Table(title="Application Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value")
        
        for key, value in sorted(config_dict.items()):
            table.add_row(key, str(value))
        
        console.print(table)

@app.command()
def benchmark():
    """Run performance benchmarks"""
    
    console.print("[blue]Running performance benchmarks...[/blue]")
    
    try:
        import time
        from statistics import mean, stdev
        
        # Get available mappings for testing
        mappings = get_available_mappings()
        if not mappings:
            console.print("[yellow]No mappings available for benchmarking[/yellow]")
            return
        
        test_mapping = mappings[0]  # Use first available mapping
        num_iterations = 10
        
        console.print(f"Testing mapping: {test_mapping}")
        console.print(f"Iterations: {num_iterations}")
        
        durations = []
        
        with Progress(console=console) as progress:
            task = progress.add_task("Running benchmark...", total=num_iterations)
            
            for i in range(num_iterations):
                start_time = time.time()
                evaluate(test_mapping)
                duration = time.time() - start_time
                durations.append(duration)
                
                progress.update(task, advance=1)
        
        # Calculate statistics
        avg_duration = mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        std_deviation = stdev(durations) if len(durations) > 1 else 0
        
        # Display results
        results_table = Table(title="Benchmark Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", justify="right")
        
        results_table.add_row("Average Duration", f"{avg_duration:.3f}s")
        results_table.add_row("Min Duration", f"{min_duration:.3f}s")
        results_table.add_row("Max Duration", f"{max_duration:.3f}s")
        results_table.add_row("Std Deviation", f"{std_deviation:.3f}s")
        results_table.add_row("Iterations", str(num_iterations))
        
        console.print(results_table)
        
        # Performance assessment
        if avg_duration < 1.0:
            console.print("[green]? Performance: Excellent (< 1s)[/green]")
        elif avg_duration < 3.0:
            console.print("[yellow]?? Performance: Good (< 3s)[/yellow]")
        else:
            console.print("[red]? Performance: Needs improvement (> 3s)[/red]")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def version():
    """Show version information"""
    
    version_info = {
        "Application": settings.app_name,
        "Version": settings.app_version,
        "Environment": settings.environment,
        "Python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "Debug Mode": settings.debug
    }
    
    table = Table(title="Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Value")
    
    for key, value in version_info.items():
        table.add_row(key, str(value))
    
    console.print(table)

if __name__ == "__main__":
    app()