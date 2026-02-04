"""CLI interface - main menu and configuration"""

from hydraulics.io.config import config
from hydraulics.ui.wizards import run_dripping_artery_wizard
from hydraulics.core.pipes import display_pipe_table
from hydraulics.core.properties import display_water_properties


def display_main_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("HYDRAULIC PIPING CALCULATION TOOL")
    print("="*60)
    print("\n1. Dripping Artery Calculator")
    print("2. Configuration")
    print("3. View Pipe Specifications")
    print("4. View Water Properties")
    print("5. Exit")
    print("\nSelect an option:")


def display_config_menu():
    """Display configuration menu"""
    print("\n" + "="*60)
    print("CONFIGURATION")
    print("="*60)
    print(f"\nCurrent settings:")
    print(f"  Pressure unit: {config.pressure_unit}")
    print(f"  Flow unit: {config.flow_unit}")
    print(f"  Length unit: {config.length_unit}")
    print("\n1. Change pressure unit")
    print("2. Change flow unit")
    print("3. Change length unit")
    print("4. Back to main menu")
    print("\nSelect an option:")


def configure_units():
    """Configuration submenu"""
    while True:
        display_config_menu()
        choice = input("> ").strip()

        if choice == "1":
            print("\nPressure units: bar, mwc (meters water column), atm")
            print("Enter unit:")
            unit = input("> ").strip().lower()
            try:
                config.set_pressure_unit(unit)
                print(f"[OK] Pressure unit set to: {unit}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            print("\nFlow units: m3/s, l/s, l/h")
            print("Enter unit:")
            unit = input("> ").strip().lower()
            try:
                config.set_flow_unit(unit)
                print(f"[OK] Flow unit set to: {unit}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "3":
            print("\nLength units: m, mm")
            print("Enter unit:")
            unit = input("> ").strip().lower()
            try:
                config.set_length_unit(unit)
                print(f"[OK] Length unit set to: {unit}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "4":
            break
        else:
            print("Invalid option. Please try again.")


def main():
    """Main menu loop"""
    while True:
        display_main_menu()
        choice = input("> ").strip()

        if choice == "1":
            run_dripping_artery_wizard()
        elif choice == "2":
            configure_units()
        elif choice == "3":
            display_pipe_table()
            input("\nPress Enter to continue...")
        elif choice == "4":
            display_water_properties()
            input("\nPress Enter to continue...")
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
