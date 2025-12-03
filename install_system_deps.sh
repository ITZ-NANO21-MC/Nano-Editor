#!/bin/bash
# Script para instalar dependencias del sistema necesarias para NanoEditor

echo "🔧 Instalando dependencias del sistema para NanoEditor..."
echo ""

# Detectar distribución de Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ No se pudo detectar la distribución de Linux"
    exit 1
fi

# Instalar según la distribución
case $OS in
    ubuntu|debian|linuxmint|pop)
        echo "📦 Detectado: Ubuntu/Debian"
        echo "Instalando python3-tk..."
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-dev
        ;;
    
    fedora|rhel|centos)
        echo "📦 Detectado: Fedora/RHEL/CentOS"
        echo "Instalando python3-tkinter..."
        sudo dnf install -y python3-tkinter python3-devel
        ;;
    
    arch|manjaro)
        echo "📦 Detectado: Arch/Manjaro"
        echo "Instalando tk..."
        sudo pacman -S --noconfirm tk
        ;;
    
    opensuse*)
        echo "📦 Detectado: openSUSE"
        echo "Instalando python3-tk..."
        sudo zypper install -y python3-tk python3-devel
        ;;
    
    *)
        echo "❌ Distribución no soportada: $OS"
        echo ""
        echo "Por favor, instala manualmente:"
        echo "  - Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  - Fedora: sudo dnf install python3-tkinter"
        echo "  - Arch: sudo pacman -S tk"
        exit 1
        ;;
esac

echo ""
echo "✅ Dependencias del sistema instaladas"
echo ""
echo "Ahora ejecuta:"
echo "  ./run.sh"
