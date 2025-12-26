# ============================================================
# SHITCOIN WHISPERER v4.1 - CORRECCIONES CRÍTICAS
# ============================================================
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox
from datetime import datetime
import threading
import time
import math
import json
import os
import random
import sys
import asyncio
from binance.client import Client
from binance.enums import *
from binance import AsyncClient

# ===================== CONFIGURACIÓN =======================
VERSION = "Shitcoin by David - v4.1 Correcciones Críticas"
CONFIG_FILE = 'config_compact.json'

# --- VALORES RECOMENDADOS DE FÁBRICA ---
DEFAULT_CONFIG = {
    'leverage_entry': "1",
    'capital_entry': "8",
    'tp_entry': "0.50",
    'sl_entry': "0.15",
    'trailing_activate_entry': "0.80",
    'trailing_distance_entry': "0.40",
    'timeframe_var': "3m",
    'break_percent_entry': "0.30",
    'max_trades_entry': "1",
    'shitcoins_per_cycle_entry': "5",
    'min_price_entry': "0.001",
    'max_price_entry': "0.5",
    'min_volume_entry': "1000000",
    'paper_var': 1,
    'trailing_var': 1,
    'break_var': 1,
    'cooldown_var': 1,
    'use_ema_var': 1,
    'use_cci_var': 1,
    'ema_fast_entry': "9",
    'ema_slow_entry': "21",
    'cci_period_entry': "20",
    'cci_upper_entry': "100",
    'cci_lower_entry': "-100",
    'momentum_loss_var': 1,
    'anti_sweep_var': 1,
    'momentum_loss_threshold_entry': "0.20",
    'momentum_loss_candles_entry': "3",
    # NUEVO: Trailing jerárquico por niveles
    'trailing_hierarchical': {
        'enabled': 0,  # 0=desactivado, 1=activado
        'levels': [
            {'activate_at': 1.0, 'move_sl_to': 0.0, 'description': 'Breakeven'},
            {'activate_at': 2.5, 'move_sl_to': 1.0, 'description': 'Protección +1%'},
            {'activate_at': 5.0, 'move_sl_to': 3.0, 'description': 'Bloqueo +3%'},
            {'activate_at': 8.0, 'move_sl_to': 'dynamic', 'trailing_distance': 2.0, 'description': 'Trailing Dinámico'}
        ]
    },
    # NUEVO: Focus Mode
    'focus_mode_enabled': 1,
}

# ============================================================
# SISTEMA DE LOGS JERÁRQUICO
# ============================================================
class LoggerProfesional:
    def __init__(self, log_widget):
        self.log_widget = log_widget
        self.filters = {
            'ERROR': True,
            'TRADE': True,
            'INFO': False,
            'DEBUG': False,
            'ESTRATEGIA': False,
            'ORDERS': True,
            'MOMENTUM': True
        }
    
    def set_filter(self, level, value):
        self.filters[level] = value
    
    def should_log(self, level):
        return self.filters.get(level, False)
    
    def log(self, message, level="INFO", color_tag="info"):
        if not self.should_log(level):
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.config(state='normal')
        
        nivel_display = f"[{level}]"
        
        emoji = ""
        if level == "ERROR":
            emoji = "❌ "
        elif level == "TRADE":
            if "ABIERTA" in message.upper():
                emoji = "💎 "
            elif "CERRADA" in message.upper():
                emoji = "📊 "
            elif "SEÑAL" in message.upper():
                emoji = "🎯 "
        elif level == "ORDERS" and ("SL" in message or "TP" in message):
            emoji = "🔒 "
        elif level == "MOMENTUM":
            emoji = "⚡ "
        
        linea = f"[{timestamp}] {nivel_display:12} {emoji}{message}\n"
        
        self.log_widget.insert('end', linea, color_tag)
        self.log_widget.config(state='disabled')
        self.log_widget.see('end')
    
    def log_separator(self, title="", level="INFO"):
        if not self.should_log(level):
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.config(state='normal')
        
        if title:
            linea = f"[{timestamp}] {'='*60}\n"
            self.log_widget.insert('end', linea, 'timestamp')
            linea = f"[{timestamp}] {title.center(60)}\n"
            self.log_widget.insert('end', linea, level.lower())
            linea = f"[{timestamp}] {'='*60}\n"
            self.log_widget.insert('end', linea, 'timestamp')
        else:
            linea = f"[{timestamp}] {'='*60}\n"
            self.log_widget.insert('end', linea, 'timestamp')
        
        self.log_widget.config(state='disabled')
        self.log_widget.see('end')

# ============================================================
# FUNCIONES DE CONFIGURACIÓN - CORREGIDAS PARA GUARDAR CHECKS
# ============================================================

def guardar_configuracion():
    """GUARDA TODOS LOS CHECKS CORRECTAMENTE"""
    config = {
        # API Keys
        'api_key': api_key_entry.get(),
        'api_secret': api_secret_entry.get(),
        
        # Variables de checkboxes (¡AHORA SE GUARDAN!)
        'paper_var': paper_var.get(),
        'trailing_var': trailing_var.get(),
        'break_var': break_var.get(),
        'cooldown_var': cooldown_var.get(),
        'use_ema_var': use_ema_var.get(),
        'use_cci_var': use_cci_var.get(),
        'momentum_loss_var': momentum_loss_var.get(),
        'anti_sweep_var': anti_sweep_var.get(),
        'anti_sweep_sensibilidad': anti_sweep_sensibilidad_var.get(),
        
        # Variables de filtros de log (¡NUEVO!)
        'show_error_var': show_error_var.get(),
        'show_trade_var': show_trade_var.get(),
        'show_info_var': show_info_var.get(),
        'show_debug_var': show_debug_var.get(),
        'show_strategy_var': show_strategy_var.get(),
        'show_orders_var': show_orders_var.get(),
        'show_momentum_var': show_momentum_var.get(),
        
        # Entradas numéricas
        'leverage_entry': leverage_entry.get(),
        'capital_entry': capital_entry.get(),
        'tp_entry': tp_entry.get(),
        'sl_entry': sl_entry.get(),
        'trailing_activate_entry': trailing_activate_entry.get(),
        'trailing_distance_entry': trailing_distance_entry.get(),
        'timeframe_var': timeframe_var.get(),
        'break_percent_entry': break_percent_entry.get(),
        'max_trades_entry': max_trades_entry.get(),
        'shitcoins_per_cycle_entry': shitcoins_per_cycle_entry.get(),
        'min_price_entry': min_price_entry.get(),
        'max_price_entry': max_price_entry.get(),
        'min_volume_entry': min_volume_entry.get(),
        
        # Configuración de estrategia
        'ema_fast_entry': DEFAULT_CONFIG['ema_fast_entry'],
        'ema_slow_entry': DEFAULT_CONFIG['ema_slow_entry'],
        'cci_period_entry': DEFAULT_CONFIG['cci_period_entry'],
        'cci_upper_entry': DEFAULT_CONFIG['cci_upper_entry'],
        'cci_lower_entry': DEFAULT_CONFIG['cci_lower_entry'],
        'momentum_loss_threshold_entry': DEFAULT_CONFIG['momentum_loss_threshold_entry'],
        'momentum_loss_candles_entry': DEFAULT_CONFIG['momentum_loss_candles_entry'],
        
        # NUEVO: Configuración de trailing jerárquico
        'trailing_hierarchical': DEFAULT_CONFIG['trailing_hierarchical'],
        
        # NUEVO: Focus Mode
        'focus_mode_enabled': DEFAULT_CONFIG.get('focus_mode_enabled', 1),
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        if logger:
            logger.log("Configuración guardada correctamente (incluye checks)", "INFO", "success")
    except Exception as e:
        if logger:
            logger.log(f"Error al guardar configuración: {e}", "ERROR", "error")

def cargar_configuracion():
    """CARGA TODOS LOS CHECKS CORRECTAMENTE"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Función auxiliar para cargar entradas
        def set_entry(entry, key):
            value = config.get(key, DEFAULT_CONFIG.get(key, entry.get()))
            if isinstance(value, str):
                value = value.strip()
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
        
        # Cargar API keys
        set_entry(api_key_entry, 'api_key')
        set_entry(api_secret_entry, 'api_secret')
        
        # Cargar checkboxes (¡ESTO ES LO QUE FALTABA!)
        paper_var.set(config.get('paper_var', DEFAULT_CONFIG['paper_var']))
        trailing_var.set(config.get('trailing_var', DEFAULT_CONFIG['trailing_var']))
        break_var.set(config.get('break_var', DEFAULT_CONFIG['break_var']))
        cooldown_var.set(config.get('cooldown_var', DEFAULT_CONFIG['cooldown_var']))
        use_ema_var.set(config.get('use_ema_var', DEFAULT_CONFIG['use_ema_var']))
        use_cci_var.set(config.get('use_cci_var', DEFAULT_CONFIG['use_cci_var']))
        momentum_loss_var.set(config.get('momentum_loss_var', DEFAULT_CONFIG['momentum_loss_var']))
        anti_sweep_var.set(config.get('anti_sweep_var', DEFAULT_CONFIG['anti_sweep_var']))
        anti_sweep_sensibilidad_var.set(config.get('anti_sweep_sensibilidad', "0.5"))
        
        # Cargar filtros de log (¡NUEVO!)
        show_error_var.set(config.get('show_error_var', 1))
        show_trade_var.set(config.get('show_trade_var', 1))
        show_info_var.set(config.get('show_info_var', 1))  # ← CAMBIADO: 0 → 1
        show_debug_var.set(config.get('show_debug_var', 0))
        show_strategy_var.set(config.get('show_strategy_var', 0))
        show_orders_var.set(config.get('show_orders_var', 1))
        show_momentum_var.set(config.get('show_momentum_var', 1))
        
        # Cargar entradas numéricas
        set_entry(leverage_entry, 'leverage_entry')
        set_entry(capital_entry, 'capital_entry')
        set_entry(tp_entry, 'tp_entry')
        set_entry(sl_entry, 'sl_entry')
        set_entry(trailing_activate_entry, 'trailing_activate_entry')
        set_entry(trailing_distance_entry, 'trailing_distance_entry')
        timeframe_var.set(config.get('timeframe_var', DEFAULT_CONFIG['timeframe_var']))
        set_entry(break_percent_entry, 'break_percent_entry')
        set_entry(max_trades_entry, 'max_trades_entry')
        set_entry(shitcoins_per_cycle_entry, 'shitcoins_per_cycle_entry')
        set_entry(min_price_entry, 'min_price_entry')
        set_entry(max_price_entry, 'max_price_entry')
        set_entry(min_volume_entry, 'min_volume_entry')
        
        # Cargar configuración de estrategia
        DEFAULT_CONFIG['ema_fast_entry'] = config.get('ema_fast_entry', DEFAULT_CONFIG['ema_fast_entry'])
        DEFAULT_CONFIG['ema_slow_entry'] = config.get('ema_slow_entry', DEFAULT_CONFIG['ema_slow_entry'])
        DEFAULT_CONFIG['cci_period_entry'] = config.get('cci_period_entry', DEFAULT_CONFIG['cci_period_entry'])
        DEFAULT_CONFIG['cci_upper_entry'] = config.get('cci_upper_entry', DEFAULT_CONFIG['cci_upper_entry'])
        DEFAULT_CONFIG['cci_lower_entry'] = config.get('cci_lower_entry', DEFAULT_CONFIG['cci_lower_entry'])
        DEFAULT_CONFIG['momentum_loss_threshold_entry'] = config.get('momentum_loss_threshold_entry', DEFAULT_CONFIG['momentum_loss_threshold_entry'])
        DEFAULT_CONFIG['momentum_loss_candles_entry'] = config.get('momentum_loss_candles_entry', DEFAULT_CONFIG['momentum_loss_candles_entry'])
        
        # NUEVO: Cargar configuración de trailing jerárquico
        DEFAULT_CONFIG['trailing_hierarchical'] = config.get('trailing_hierarchical', DEFAULT_CONFIG['trailing_hierarchical'])
        
        # NUEVO: Cargar Focus Mode
        DEFAULT_CONFIG['focus_mode_enabled'] = config.get('focus_mode_enabled', 1)
        
        if logger:
            logger.log("Configuración cargada desde archivo (checks incluidos + trailing jerárquico)", "INFO", "success")
    except FileNotFoundError:
        if logger:
            logger.log("Archivo de configuración no encontrado. Usando valores de fábrica", "INFO", "warning")
    except Exception as e:
        if logger:
            logger.log(f"Error al cargar configuración: {e}", "ERROR", "error")

def reset_a_fabrica():
    def set_entry(entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
    
    set_entry(leverage_entry, DEFAULT_CONFIG['leverage_entry'])
    set_entry(capital_entry, DEFAULT_CONFIG['capital_entry'])
    set_entry(tp_entry, DEFAULT_CONFIG['tp_entry'])
    set_entry(sl_entry, DEFAULT_CONFIG['sl_entry'])
    set_entry(trailing_activate_entry, DEFAULT_CONFIG['trailing_activate_entry'])
    set_entry(trailing_distance_entry, DEFAULT_CONFIG['trailing_distance_entry'])
    timeframe_var.set(DEFAULT_CONFIG['timeframe_var'])
    set_entry(break_percent_entry, DEFAULT_CONFIG['break_percent_entry'])
    set_entry(max_trades_entry, DEFAULT_CONFIG['max_trades_entry'])
    set_entry(shitcoins_per_cycle_entry, DEFAULT_CONFIG['shitcoins_per_cycle_entry'])
    set_entry(min_price_entry, DEFAULT_CONFIG['min_price_entry'])
    set_entry(max_price_entry, DEFAULT_CONFIG['max_price_entry'])
    set_entry(min_volume_entry, DEFAULT_CONFIG['min_volume_entry'])
    
    # Resetear checkboxes a valores de fábrica
    paper_var.set(DEFAULT_CONFIG['paper_var'])
    trailing_var.set(DEFAULT_CONFIG['trailing_var'])
    break_var.set(DEFAULT_CONFIG['break_var'])
    cooldown_var.set(DEFAULT_CONFIG['cooldown_var'])
    use_ema_var.set(DEFAULT_CONFIG['use_ema_var'])
    use_cci_var.set(DEFAULT_CONFIG['use_cci_var'])
    momentum_loss_var.set(DEFAULT_CONFIG['momentum_loss_var'])
    anti_sweep_var.set(DEFAULT_CONFIG['anti_sweep_var'])
    anti_sweep_sensibilidad_var.set("0.5")
    
    # Resetear filtros de log a valores de fábrica (¡NUEVO!)
    show_error_var.set(1)
    show_trade_var.set(1)
    show_info_var.set(1)  # ← CAMBIADO: 0 → 1
    show_debug_var.set(0)
    show_strategy_var.set(0)
    show_orders_var.set(1)
    show_momentum_var.set(1)
    
    # NUEVO: Resetear trailing jerárquico a valores de fábrica
    DEFAULT_CONFIG['trailing_hierarchical'] = {
        'enabled': 0,
        'levels': [
            {'activate_at': 1.0, 'move_sl_to': 0.0, 'description': 'Breakeven'},
            {'activate_at': 2.5, 'move_sl_to': 1.0, 'description': 'Protección +1%'},
            {'activate_at': 5.0, 'move_sl_to': 3.0, 'description': 'Bloqueo +3%'},
            {'activate_at': 8.0, 'move_sl_to': 'dynamic', 'trailing_distance': 2.0, 'description': 'Trailing Dinámico'}
        ]
    }
    
    # NUEVO: Resetear Focus Mode
    DEFAULT_CONFIG['focus_mode_enabled'] = 1
    
    if logger:
        logger.log("Valores de configuración reiniciados a valores de fábrica", "INFO")

def seleccionar_carpeta_reportes():
    global report_folder
    folder = filedialog.askdirectory()
    if folder:
        report_folder = folder
        if logger:
            logger.log(f"Carpeta de reportes seleccionada: {report_folder}", "INFO", "report")

# ============================================================
# FUNCIONES DE REPORTES
# ============================================================
def generar_reporte_diario():
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(report_folder, f"reporte_detallado_{hoy}.txt")
    
    try:
        trades_hoy = [t for t in trade_history if t['fecha'].startswith(hoy)]
        
        if not trades_hoy:
            reporte_data = [
                f"{'='*50}",
                f"REPORTE DIARIO - {hoy}",
                f"{'='*50}",
                f"Versión: {VERSION}",
                f"Horario generación: {datetime.now().strftime('%H:%M:%S')}",
                f"",
                f"📊 RESUMEN DEL DÍA:",
                f"Total operaciones: 0",
                f"Operaciones ganadoras: 0 (0.00%)",
                f"Operaciones perdedoras: 0 (0.00%)",
                f"P&L neto: 0.000000 USDT",
                f"ROI promedio: 0.00%",
                f"",
                f"⚠️ No se registraron operaciones hoy.",
                f"{'='*50}"
            ]
        else:
            total_trades = len(trades_hoy)
            ganadoras = sum(1 for t in trades_hoy if t['pnl_usdt'] > 0)
            perdedoras = sum(1 for t in trades_hoy if t['pnl_usdt'] < 0)
            pnl_neto = sum(t['pnl_usdt'] for t in trades_hoy)
            roi_promedio = sum(t['roi_percent'] for t in trades_hoy) / total_trades if total_trades > 0 else 0
            
            reporte_data = [
                f"{'='*50}",
                f"REPORTE DIARIO DETALLADO - {hoy}",
                f"{'='*50}",
                f"Versión: {VERSION}",
                f"Horario generación: {datetime.now().strftime('%H:%M:%S')}",
                f"",
                f"📊 RESUMEN DEL DÍA:",
                f"Total operaciones: {total_trades}",
                f"Operaciones ganadoras: {ganadoras} ({ganadoras/total_trades*100:.2f}%)",
                f"Operaciones perdedoras: {perdedoras} ({perdedoras/total_trades*100:.2f}%)",
                f"P&L neto: {pnl_neto:.6f} USDT",
                f"ROI promedio: {roi_promedio:.2f}%",
                f"Mejor trade: {max(trades_hoy, key=lambda x: x['pnl_usdt'])['pnl_usdt']:.6f} USDT" if trades_hoy else "N/A",
                f"Peor trade: {min(trades_hoy, key=lambda x: x['pnl_usdt'])['pnl_usdt']:.6f} USDT" if trades_hoy else "N/A",
                f"",
                f"📈 OPERACIONES INDIVIDUALES:",
                f""
            ]
            
            for i, trade in enumerate(trades_hoy, 1):
                signo = "+" if trade['pnl_usdt'] > 0 else ""
                resultado = "GANANCIA" if trade['pnl_usdt'] > 0 else "PERDIDA" if trade['pnl_usdt'] < 0 else "BREAKEVEN"
                
                reporte_data.extend([
                    f"{'='*50}",
                    f"OPERACIÓN #{i} - {resultado}",
                    f"{'='*50}",
                    f"Fecha: {trade['fecha']}",
                    f"Par: {trade['symbol']}",
                    f"Tipo: {trade['tipo']}",
                    f"Entrada: {trade['entry_price']:.8f}",
                    f"Salida: {trade['exit_price']:.8f}",
                    f"ROI: {signo}{trade['roi_percent']:.2f}%",
                    f"Resultado (PnL): {trade['pnl_usdt']:.8f} USDT",
                    f"Estrategia: {trade['estrategia']}",
                    f"Motivo: {trade['motivo']}",
                    f"Duración: {trade['duracion']}",
                    f""
                ])
            
            reporte_data.extend([
                f"{'='*50}",
                f"FIN DEL REPORTE",
                f"{'='*50}"
            ])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(reporte_data))
        
        logger.log(f"Reporte diario generado: {filename}", "INFO", "report")
        
        if trades_hoy:
            pnl_color = "profit" if pnl_neto > 0 else "error" if pnl_neto < 0 else "info"
            logger.log(f"RESUMEN: {total_trades} trades | Ganadoras: {ganadoras} | Perdedoras: {perdedoras} | P&L Neto: {pnl_neto:.6f} USDT", "INFO", pnl_color)
        
        return True
        
    except Exception as e:
        logger.log(f"Error al generar reporte: {e}", "ERROR", "error")
        return False

# ============================================================
# GUI PRINCIPAL - INTERFAZ PROFESIONAL CON PANEL DE ESTADO
# ============================================================
root = tk.Tk()
root.title(f"Shitcoin Whisperer Professional {VERSION}")
root.geometry("1300x720")
root.configure(bg="#1e1e1e")

# Variable global para logger
logger = None

# VARIABLE GLOBAL PARA CARPETA DE REPORTES
report_folder = "reportes"

# VARIABLES GLOBALES DEL BOT
client = None
bot_running = False
bot_lock = threading.Lock()
stablecoins = ['USDT','BUSD','USDC','DAI','TUSD','USDP','USDD']
active_trades = {}
symbols_with_positions = set()
last_signal_time = {}
all_shitcoins = []
last_coin_refresh = 0
COIN_REFRESH_INTERVAL = 300
trade_history = []

# VARIABLES PARA EL PANEL
status_vars = {}
led_canvas = None
led = None
led_status = "off"

# CREAR FRAME PRINCIPAL CON DOS COLUMNAS
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill='both', expand=True, padx=10, pady=5)

# COLUMNA IZQUIERDA: CONFIGURACIÓN
left_frame = tk.Frame(main_frame, bg="#1e1e1e")
left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

# FRAME CONFIGURACIONES
config_frame = tk.LabelFrame(left_frame, text="CONFIGURACIÓN", font=('Arial',10,'bold'),
                             bg='#2c2c2c', fg='#f0f0f0', padx=10, pady=10)
config_frame.pack(fill='both', expand=True)

# API Keys
tk.Label(config_frame, text="API Key:", bg='#2c2c2c', fg='#e0e0e0').grid(row=0,column=0,sticky='w', pady=2)
api_key_entry = tk.Entry(config_frame, width=40, show="*")
api_key_entry.grid(row=0,column=1,sticky='w', pady=2)

tk.Label(config_frame, text="API Secret:", bg='#2c2c2c', fg='#e0e0e0').grid(row=1,column=0,sticky='w', pady=2)
api_secret_entry = tk.Entry(config_frame, width=40, show="*")
api_secret_entry.grid(row=1,column=1,sticky='w', pady=2)

# MODO PAPER TRADING
paper_var = tk.IntVar(value=DEFAULT_CONFIG['paper_var'])
paper_check = tk.Checkbutton(
    config_frame,
    text="MODO PAPER TRADING (Testnet)",
    variable=paper_var,
    bg='#2c2c2c',
    fg='#2ecc71',
    selectcolor='#2c2c2c',
    font=('Arial', 9)
)
paper_check.grid(row=0,column=2,sticky='w', padx=(20,0), pady=2, rowspan=2)

# Parámetros básicos
tk.Label(config_frame, text="Leverage:", bg='#2c2c2c', fg='#e0e0e0').grid(row=2,column=0,sticky='w', pady=2)
leverage_entry = tk.Entry(config_frame, width=10)
leverage_entry.insert(0, DEFAULT_CONFIG['leverage_entry'])
leverage_entry.grid(row=2,column=1,sticky='w', pady=2)

tk.Label(config_frame, text="Capital por trade (USDT):", bg='#2c2c2c', fg='#e0e0e0').grid(row=3,column=0,sticky='w', pady=2)
capital_entry = tk.Entry(config_frame, width=10)
capital_entry.insert(0, DEFAULT_CONFIG['capital_entry'])
capital_entry.grid(row=3,column=1,sticky='w', pady=2)

tk.Label(config_frame, text="TP ROI %:", bg='#2c2c2c', fg='#e0e0e0').grid(row=2,column=2,sticky='w', padx=(20,0), pady=2)
tp_entry = tk.Entry(config_frame, width=6)
tp_entry.insert(0, DEFAULT_CONFIG['tp_entry'])
tp_entry.grid(row=2,column=3,sticky='w', pady=7)

tk.Label(config_frame, text="SL ROI %:", bg='#2c2c2c', fg='#e0e0e0').grid(row=3,column=2,sticky='w', padx=(20,0), pady=2)
sl_entry = tk.Entry(config_frame, width=6)
sl_entry.insert(0, DEFAULT_CONFIG['sl_entry'])
sl_entry.grid(row=3,column=3,sticky='w', pady=2)

# TRAILING STOP
trailing_var = tk.IntVar(value=DEFAULT_CONFIG['trailing_var'])
trailing_check = tk.Checkbutton(
    config_frame,
    text="ACTIVAR TRAILING STOP (Piramidal)",
    variable=trailing_var,
    bg='#2c2c2c',
    fg='#1abc9c',
    selectcolor='#2c2c2c',
    font=('Arial', 9, 'bold')
)
trailing_check.grid(row=4,column=0,columnspan=2,sticky='w', pady=(10,2))

tk.Label(config_frame, text="Activar Trailing en % ROI:", bg='#2c2c2c', fg='#1abc9c').grid(row=5,column=0,sticky='w', pady=2)
trailing_activate_entry = tk.Entry(config_frame, width=10)
trailing_activate_entry.insert(0, DEFAULT_CONFIG['trailing_activate_entry'])
trailing_activate_entry.grid(row=5,column=1,sticky='w', pady=2)

tk.Label(config_frame, text="Distancia Trailing % ROI:", bg='#2c2c2c', fg='#1abc9c').grid(row=5,column=2,sticky='w', padx=(5,0), pady=2)
trailing_distance_entry = tk.Entry(config_frame, width=6)
trailing_distance_entry.insert(0, DEFAULT_CONFIG['trailing_distance_entry'])
trailing_distance_entry.grid(row=5,column=3,sticky='w', pady=2)

# SELECTOR DE TEMPORALIDAD
tk.Label(config_frame, text="Temporalidad:", bg='#2c2c2c', fg='#e0e0e0').grid(row=6,column=0,sticky='w', pady=2)
timeframe_options = ["1m", "3m", "5m", "15m", "30m"]
timeframe_var = tk.StringVar(value=DEFAULT_CONFIG['timeframe_var'])
timeframe_combo = ttk.Combobox(config_frame, textvariable=timeframe_var,
                              values=timeframe_options, width=8, state="readonly")
timeframe_combo.grid(row=6,column=1,sticky='w', pady=2)

# BREAK-EVEN
break_var = tk.IntVar(value=DEFAULT_CONFIG['break_var'])
break_check = tk.Checkbutton(
    config_frame,
    text="Activar Break-Even (Primera capa de protección)",
    variable=break_var,
    bg='#2c2c2c',
    fg='#9b59b6',
    selectcolor='#2c2c2c'
)
break_check.grid(row=7,column=0,sticky='w', pady=(10,2), columnspan=2)

tk.Label(config_frame, text="% ROI para mover SL a Break-Even", bg='#2c2c2c', fg='#9b59b6').grid(row=7,column=2,sticky='w', padx=(5,0), pady=2)
break_percent_entry = tk.Entry(config_frame, width=6)
break_percent_entry.insert(0, DEFAULT_CONFIG['break_percent_entry'])
break_percent_entry.grid(row=7,column=3,sticky='w', pady=2)

tk.Label(config_frame, text="Max operaciones simultáneas:", bg='#2c2c2c', fg='#e0e0e0').grid(row=8,column=0,sticky='w', pady=2)
max_trades_entry = tk.Entry(config_frame, width=10)
max_trades_entry.insert(0, DEFAULT_CONFIG['max_trades_entry'])
max_trades_entry.grid(row=8,column=1,sticky='w', pady=2)

# NUEVOS CHECKBOXES v3.0 CON SENSIBILIDAD
additional_checks_frame = tk.Frame(config_frame, bg='#2c2c2c')
additional_checks_frame.grid(row=9, column=0, columnspan=4, sticky='w', pady=(5, 2))

momentum_loss_var = tk.IntVar(value=DEFAULT_CONFIG['momentum_loss_var'])
momentum_loss_check = tk.Checkbutton(
    additional_checks_frame,
    text="Momentum Loss",
    variable=momentum_loss_var,
    bg='#2c2c2c',
    fg='#e67e22',
    selectcolor='#2c2c2c',
    font=('Arial', 9)
)
momentum_loss_check.pack(side='left', padx=(0, 20))

anti_sweep_var = tk.IntVar(value=DEFAULT_CONFIG['anti_sweep_var'])
anti_sweep_check = tk.Checkbutton(
    additional_checks_frame,
    text="Anti-Sweep MM",
    variable=anti_sweep_var,
    bg='#2c2c2c',
    fg='#3498db',
    selectcolor='#2c2c2c',
    font=('Arial', 9)
)
anti_sweep_check.pack(side='left', padx=(0, 5))

# SENSIBILIDAD ANTI-SWEEP (NUEVO)
tk.Label(additional_checks_frame, text="Sens (%):", bg='#2c2c2c', fg='#3498db', font=('Arial', 8)).pack(side='left', padx=(5, 2))
anti_sweep_sensibilidad_var = tk.StringVar(value="0.5")  # Valor por defecto 0.5%
anti_sweep_sensibilidad_entry = tk.Entry(additional_checks_frame, width=5, textvariable=anti_sweep_sensibilidad_var, bg='#3c3c3c', fg='white', justify='center')
anti_sweep_sensibilidad_entry.pack(side='left')

# CONFIGURACIÓN SHITCOIN ROTATOR
rotator_frame = tk.LabelFrame(config_frame, text="SHITCOIN ROTATOR", font=('Arial',9,'bold'),
                              bg='#2c2c2c', fg='#f39c12', padx=10, pady=5)
rotator_frame.grid(row=10, column=0, columnspan=4, sticky='ew', pady=(10,5))

tk.Label(rotator_frame, text="Shitcoins por ciclo:", bg='#2c2c2c', fg='#f39c12').grid(row=0,column=0,sticky='w', pady=2)
shitcoins_per_cycle_entry = tk.Entry(rotator_frame, width=10)
shitcoins_per_cycle_entry.insert(0, DEFAULT_CONFIG['shitcoins_per_cycle_entry'])
shitcoins_per_cycle_entry.grid(row=0,column=1,sticky='w', pady=2)

tk.Label(rotator_frame, text="Mín. precio (USDT):", bg='#2c2c2c', fg='#f39c12').grid(row=0,column=2,sticky='w', padx=(10,0), pady=2)
min_price_entry = tk.Entry(rotator_frame, width=10)
min_price_entry.insert(0, DEFAULT_CONFIG['min_price_entry'])
min_price_entry.grid(row=0,column=3,sticky='w', pady=2)

tk.Label(rotator_frame, text="Máx. precio (USDT):", bg='#2c2c2c', fg='#f39c12').grid(row=1,column=0,sticky='w', pady=2)
max_price_entry = tk.Entry(rotator_frame, width=10)
max_price_entry.insert(0, DEFAULT_CONFIG['max_price_entry'])
max_price_entry.grid(row=1,column=1,sticky='w', pady=2)

tk.Label(rotator_frame, text="Mín. volumen 24h (USDT):", bg='#2c2c2c', fg='#f39c12').grid(row=1,column=2,sticky='w', padx=(10,0), pady=2)
min_volume_entry = tk.Entry(rotator_frame, width=10)
min_volume_entry.insert(0, DEFAULT_CONFIG['min_volume_entry'])
min_volume_entry.grid(row=1,column=3,sticky='w', pady=2)

cooldown_var = tk.IntVar(value=DEFAULT_CONFIG['cooldown_var'])
cooldown_check = tk.Checkbutton(
    rotator_frame,
    text="Cooldown 90s entre trades",
    variable=cooldown_var,
    bg='#2c2c2c',
    fg='#f39c12',
    selectcolor='#2c2c2c'
)
cooldown_check.grid(row=2,column=0,columnspan=2,sticky='w', pady=(5,0))

# ESTRATEGIA DE TRADING
strategy_frame = tk.LabelFrame(config_frame, text="ESTRATEGIA DE TRADING", font=('Arial',9,'bold'),
                              bg='#2c2c2c', fg='#3498db', padx=10, pady=5)
strategy_frame.grid(row=11, column=0, columnspan=4, sticky='ew', pady=(10,5))

use_ema_var = tk.IntVar(value=DEFAULT_CONFIG['use_ema_var'])
use_cci_var = tk.IntVar(value=DEFAULT_CONFIG['use_cci_var'])

strategy_main_frame = tk.Frame(strategy_frame, bg='#2c2c2c')
strategy_main_frame.pack(fill='x', expand=True)

checkbox_frame = tk.Frame(strategy_main_frame, bg='#2c2c2c')
checkbox_frame.pack(side='left', fill='y', padx=(0, 20))

button_strategy_frame = tk.Frame(strategy_main_frame, bg='#2c2c2c')
button_strategy_frame.pack(side='right', fill='y')

ema_check = tk.Checkbutton(
    checkbox_frame,
    text="ACTIVAR EMA",
    variable=use_ema_var,
    bg='#2c2c2c',
    fg='#e74c3c',
    selectcolor='#2c2c2c',
    font=('Arial', 9)
)
ema_check.pack(side='left', padx=(0, 15))

cci_check = tk.Checkbutton(
    checkbox_frame,
    text="ACTIVAR CCI",
    variable=use_cci_var,
    bg='#2c2c2c',
    fg='#2ecc71',
    selectcolor='#2c2c2c',
    font=('Arial', 9)
)
cci_check.pack(side='left', padx=(0, 20))

def abrir_config_estrategia():
    config_window = tk.Toplevel(root)
    config_window.title("Configuración de Estrategia")
    config_window.geometry("400x450")
    config_window.configure(bg='#2c2c2c')
    config_window.grab_set()
    config_window.resizable(False, False)
    
    main_frame = tk.Frame(config_window, bg='#2c2c2c', padx=20, pady=15)
    main_frame.pack(fill='both', expand=True)
    
    ema_frame = tk.LabelFrame(main_frame, text="EMA Settings", font=('Arial', 9, 'bold'),
                              bg='#2c2c2c', fg='#e74c3c', padx=10, pady=10)
    ema_frame.pack(fill='x', pady=(0, 10))
    
    tk.Label(ema_frame, text="EMA Rápida:", bg='#2c2c2c', fg='#e0e0e0', font=('Arial', 9)).grid(row=0, column=0, sticky='w', pady=5)
    ema_fast_entry_config = tk.Entry(ema_frame, width=12, bg='#3c3c3c', fg='white', insertbackground='white')
    ema_fast_entry_config.insert(0, DEFAULT_CONFIG['ema_fast_entry'])
    ema_fast_entry_config.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
    
    tk.Label(ema_frame, text="EMA Lenta:", bg='#2c2c2c', fg='#e0e0e0', font=('Arial', 9)).grid(row=1, column=0, sticky='w', pady=5)
    ema_slow_entry_config = tk.Entry(ema_frame, width=12, bg='#3c3c3c', fg='white', insertbackground='white')
    ema_slow_entry_config.insert(0, DEFAULT_CONFIG['ema_slow_entry'])
    ema_slow_entry_config.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
    
    cci_frame = tk.LabelFrame(main_frame, text="CCI Settings", font=('Arial', 9, 'bold'),
                              bg='#2c2c2c', fg='#2ecc71', padx=10, pady=10)
    cci_frame.pack(fill='x', pady=(0, 10))
    
    tk.Label(cci_frame, text="Período CCI:", bg='#2c2c2c', fg='#e0e0e0', font=('Arial', 9)).grid(row=0, column=0, sticky='w', pady=5)
    cci_period_entry_config = tk.Entry(cci_frame, width=12, bg='#3c3c3c', fg='white', insertbackground='white')
    cci_period_entry_config.insert(0, DEFAULT_CONFIG['cci_period_entry'])
    cci_period_entry_config.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
    
    tk.Label(cci_frame, text="Límite Superior:", bg='#2c2c2c', fg='#e0e0e0', font=('Arial', 9)).grid(row=1, column=0, sticky='w', pady=5)
    cci_upper_entry_config = tk.Entry(cci_frame, width=12, bg='#3c3c3c', fg='white', insertbackground='white')
    cci_upper_entry_config.insert(0, DEFAULT_CONFIG['cci_upper_entry'])
    cci_upper_entry_config.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
    
    tk.Label(cci_frame, text="Límite Inferior:", bg='#2c2c2c', fg='#e0e0e0', font=('Arial', 9)).grid(row=2, column=0, sticky='w', pady=5)
    cci_lower_entry_config = tk.Entry(cci_frame, width=12, bg='#3c3c3c', fg='white', insertbackground='white')
    cci_lower_entry_config.insert(0, DEFAULT_CONFIG['cci_lower_entry'])
    cci_lower_entry_config.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
    
    momentum_frame = tk.LabelFrame(main_frame, text="Momentum Loss Settings", 
                                  font=('Arial', 9, 'bold'),
                                  bg='#2c2c2c', fg='#e67e22', padx=10, pady=10)
    momentum_frame.pack(fill='x', pady=(0, 15))
    
    tk.Label(momentum_frame, text="% Mínimo esperado:", bg='#2c2c2c', fg='#e0e0e0', 
             font=('Arial', 9)).grid(row=0, column=0, sticky='w', pady=5)
    momentum_loss_threshold_entry_config = tk.Entry(momentum_frame, width=12, 
                                                   bg='#3c3c3c', fg='white', 
                                                   insertbackground='white')
    momentum_loss_threshold_entry_config.insert(0, DEFAULT_CONFIG['momentum_loss_threshold_entry'])
    momentum_loss_threshold_entry_config.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
    
    tk.Label(momentum_frame, text="Velas para evaluar:", bg='#2c2c2c', fg='#e0e0e0', 
             font=('Arial', 9)).grid(row=1, column=0, sticky='w', pady=5)
    momentum_loss_candles_entry_config = tk.Entry(momentum_frame, width=12, 
                                                 bg='#3c3c3c', fg='white', 
                                                 insertbackground='white')
    momentum_loss_candles_entry_config.insert(0, DEFAULT_CONFIG['momentum_loss_candles_entry'])
    momentum_loss_candles_entry_config.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
    
    def guardar_config_estrategia():
        try:
            ema_fast = int(ema_fast_entry_config.get())
            ema_slow = int(ema_slow_entry_config.get())
            if ema_fast <= 0 or ema_slow <= 0:
                raise ValueError("Las EMAs deben ser mayores a 0")
            if ema_fast >= ema_slow:
                raise ValueError("EMA rápida debe ser menor que EMA lenta")
            
            cci_period = int(cci_period_entry_config.get())
            cci_upper = int(cci_upper_entry_config.get())
            cci_lower = int(cci_lower_entry_config.get())
            if cci_period <= 0:
                raise ValueError("Período CCI debe ser mayor a 0")
            if cci_upper <= cci_lower:
                raise ValueError("Límite superior debe ser mayor que límite inferior")
            
            momentum_threshold = float(momentum_loss_threshold_entry_config.get())
            momentum_candles = int(momentum_loss_candles_entry_config.get())
            if momentum_threshold <= 0:
                raise ValueError("Momentum Loss % debe ser mayor a 0")
            if momentum_candles <= 0:
                raise ValueError("Velas para evaluar debe ser mayor a 0")
            
            DEFAULT_CONFIG['ema_fast_entry'] = str(ema_fast)
            DEFAULT_CONFIG['ema_slow_entry'] = str(ema_slow)
            DEFAULT_CONFIG['cci_period_entry'] = str(cci_period)
            DEFAULT_CONFIG['cci_upper_entry'] = str(cci_upper)
            DEFAULT_CONFIG['cci_lower_entry'] = str(cci_lower)
            DEFAULT_CONFIG['momentum_loss_threshold_entry'] = str(momentum_threshold)
            DEFAULT_CONFIG['momentum_loss_candles_entry'] = str(momentum_candles)
            
            guardar_configuracion()
            
            if logger:
                logger.log("Configuración de estrategia guardada correctamente", "INFO", "success")
            config_window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", f"Dato inválido: {str(e)}\n\nPor favor ingresa valores numéricos válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    btn_frame = tk.Frame(main_frame, bg='#2c2c2c', pady=10)
    btn_frame.pack(fill='x', pady=(5, 0))
    
    btn_guardar = tk.Button(btn_frame, text="GUARDAR", command=guardar_config_estrategia,
                           bg='#3498db', fg='#ffffff', font=('Arial', 9, 'bold'),
                           width=12, height=1, relief='raised', bd=1)
    btn_guardar.pack(side='left', padx=(0, 10))
    
    btn_cancelar = tk.Button(btn_frame, text="CANCELAR", command=config_window.destroy,
                            bg='#e74c3c', fg='#ffffff', font=('Arial', 9, 'bold'),
                            width=12, height=1, relief='raised', bd=1)
    btn_cancelar.pack(side='left')
    
    config_window.update_idletasks()
    width = config_window.winfo_width()
    height = config_window.winfo_height()
    x = (config_window.winfo_screenwidth() // 2) - (width // 2)
    y = (config_window.winfo_screenheight() // 2) - (height // 2)
    config_window.geometry(f'{width}x{height}+{x}+{y}')

# ============================================================
# FUNCIÓN CORREGIDA: CONFIGURACIÓN TRAILING JERÁRQUICO
# ============================================================
def abrir_config_trailing_niveles():
    config_window = tk.Toplevel(root)
    config_window.title("Configuración Trailing Jerárquico")
    config_window.geometry("520x450")
    config_window.configure(bg='#2c2c2c')
    config_window.grab_set()
    config_window.resizable(False, False)
    
    main_frame = tk.Frame(config_window, bg='#2c2c2c', padx=15, pady=12)
    main_frame.pack(fill='both', expand=True)
    
    # Título
    tk.Label(main_frame, text="TRAILING STOP JERÁRQUICO POR NIVELES", 
            font=('Arial', 11, 'bold'), bg='#2c2c2c', fg='#1abc9c').pack(pady=(0, 12))
    
    # Checkbox activar/desactivar
    hierarchical_enabled_var = tk.IntVar(value=DEFAULT_CONFIG['trailing_hierarchical']['enabled'])
    
    enabled_frame = tk.Frame(main_frame, bg='#2c2c2c')
    enabled_frame.pack(fill='x', pady=(0, 12))
    
    tk.Checkbutton(enabled_frame, text="ACTIVAR Trailing Jerárquico", 
                  variable=hierarchical_enabled_var,
                  bg='#2c2c2c', fg='#1abc9c', selectcolor='#2c2c2c',
                  font=('Arial', 9, 'bold')).pack(side='left')
    
    # Frame para niveles
    levels_frame = tk.LabelFrame(main_frame, text="CONFIGURACIÓN DE NIVELES", 
                                font=('Arial', 9, 'bold'),
                                bg='#2c2c2c', fg='#3498db', padx=10, pady=8)
    levels_frame.pack(fill='both', expand=True, pady=(0, 12))
    
    # Cabecera de tabla - CENTRADA VERTICALMENTE
    header_frame = tk.Frame(levels_frame, bg='#2c2c2c')
    header_frame.pack(fill='x', pady=(0, 8))
    
    # Configurar pesos de columnas para expansión uniforme
    header_frame.grid_columnconfigure(0, weight=1, minsize=60)
    header_frame.grid_columnconfigure(1, weight=1, minsize=100)
    header_frame.grid_columnconfigure(2, weight=1, minsize=120)
    header_frame.grid_columnconfigure(3, weight=1, minsize=130)
    
    tk.Label(header_frame, text="Nivel", bg='#2c2c2c', fg='#f0f0f0', 
            font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=2, sticky='nsew')
    tk.Label(header_frame, text="Activar en", bg='#2c2c2c', fg='#f0f0f0',
            font=('Arial', 9, 'bold')).grid(row=0, column=1, padx=2, sticky='nsew')
    tk.Label(header_frame, text="Mover SL a", bg='#2c2c2c', fg='#f0f0f0',
            font=('Arial', 9, 'bold')).grid(row=0, column=2, padx=2, sticky='nsew')
    tk.Label(header_frame, text="Descripción", bg='#2c2c2c', fg='#f0f0f0',
            font=('Arial', 9, 'bold')).grid(row=0, column=3, padx=2, sticky='nsew')
    
    # Campos para 4 niveles
    entries = []
    user_levels = DEFAULT_CONFIG['trailing_hierarchical']['levels']
    
    # Descripciones fijas (no editables)
    descripciones_fijas = ['Breakeven', 'Protección +1%', 'Bloqueo +3%', 'Trailing Dinámico']
    
    for i in range(4):
        level_frame = tk.Frame(levels_frame, bg='#2c2c2c', height=30)
        level_frame.pack(fill='x', pady=3, expand=True)
        level_frame.pack_propagate(False)  # Mantener altura fija
        
        # Configurar pesos de columnas para centrado
        level_frame.grid_columnconfigure(0, weight=1, minsize=60)
        level_frame.grid_columnconfigure(1, weight=1, minsize=100)
        level_frame.grid_columnconfigure(2, weight=1, minsize=120)
        level_frame.grid_columnconfigure(3, weight=1, minsize=130)
        
        # Número de nivel con color - CENTRADO
        nivel_colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
        nivel_label = tk.Label(level_frame, text=f"Nivel {i+1}", 
                              bg='#2c2c2c', fg=nivel_colors[i], font=('Arial', 9))
        nivel_label.grid(row=0, column=0, padx=2, sticky='nsew')
        
        # Activar en % - CENTRADO
        activate_container = tk.Frame(level_frame, bg='#2c2c2c')
        activate_container.grid(row=0, column=1, padx=2, sticky='nsew')
        
        activate_entry = tk.Entry(activate_container, width=8, bg='#3c3c3c', fg='white', 
                                 justify='center', font=('Arial', 9))
        activate_entry.insert(0, str(user_levels[i]['activate_at']))
        activate_entry.pack(side='left', pady=2)
        
        tk.Label(activate_container, text="%", bg='#2c2c2c', fg='#aaaaaa', 
                font=('Arial', 9)).pack(side='left', padx=(2, 0), pady=2)
        
        # Mover SL a % (o "dynamic") - CENTRADO
        move_container = tk.Frame(level_frame, bg='#2c2c2c')
        move_container.grid(row=0, column=2, padx=2, sticky='nsew')
        
        # Manejar correctamente el valor de move_sl_to
        move_sl_to_val = user_levels[i]['move_sl_to']
        
        if isinstance(move_sl_to_val, str) and move_sl_to_val.lower() == 'dynamic':
            # PARA ÚLTIMO NIVEL: Trailing dinámico
            tk.Label(move_container, text="±", bg='#2c2c2c', fg='#1abc9c', 
                    font=('Arial', 9, 'bold')).pack(side='left', pady=2)
            
            distance_entry = tk.Entry(move_container, width=6, bg='#3c3c3c', fg='white', 
                                     justify='center', font=('Arial', 9))
            distance_entry.insert(0, str(user_levels[i].get('trailing_distance', 2.0)))
            distance_entry.pack(side='left', padx=(2, 0), pady=2)
            
            tk.Label(move_container, text="% ROI", bg='#2c2c2c', fg='#aaaaaa', 
                    font=('Arial', 9)).pack(side='left', pady=2)
            
            entries.append({
                'activate_entry': activate_entry,
                'distance_entry': distance_entry,
                'is_dynamic': True
            })
        else:
            # Para niveles no dinámicos
            move_entry = tk.Entry(move_container, width=8, bg='#3c3c3c', fg='white', 
                                 justify='center', font=('Arial', 9))
            move_entry.insert(0, str(move_sl_to_val))
            move_entry.pack(side='left', pady=2)
            
            tk.Label(move_container, text="% ROI", bg='#2c2c2c', fg='#aaaaaa', 
                    font=('Arial', 9)).pack(side='left', padx=(2, 0), pady=2)
            
            entries.append({
                'activate_entry': activate_entry,
                'move_entry': move_entry,
                'distance_entry': None,
                'is_dynamic': False
            })
        
        # Descripción NO EDITABLE - Fija y CENTRADA
        desc_label = tk.Label(level_frame, text=descripciones_fijas[i], 
                             bg='#2c2c2c', fg='#aaaaaa', font=('Arial', 9))
        desc_label.grid(row=0, column=3, padx=2, sticky='nsew')
    
    def cargar_valores_por_defecto():
        default_levels = DEFAULT_CONFIG['trailing_hierarchical']['levels']
        for i, entry_dict in enumerate(entries):
            entry_dict['activate_entry'].delete(0, tk.END)
            entry_dict['activate_entry'].insert(0, str(default_levels[i]['activate_at']))
            
            move_sl_to_val = default_levels[i]['move_sl_to']
            
            if isinstance(move_sl_to_val, str) and move_sl_to_val.lower() == 'dynamic':
                if entry_dict['distance_entry']:
                    entry_dict['distance_entry'].delete(0, tk.END)
                    entry_dict['distance_entry'].insert(0, str(default_levels[i].get('trailing_distance', 2.0)))
            else:
                if 'move_entry' in entry_dict:
                    entry_dict['move_entry'].delete(0, tk.END)
                    entry_dict['move_entry'].insert(0, str(move_sl_to_val))
    
    def guardar_config_trailing():
        try:
            # Validar entradas
            levels = []
            for i, entry_dict in enumerate(entries):
                activate_at = float(entry_dict['activate_entry'].get())
                
                if entry_dict['is_dynamic']:
                    trailing_distance = 2.0
                    if entry_dict['distance_entry']:
                        try:
                            trailing_distance = float(entry_dict['distance_entry'].get())
                        except:
                            trailing_distance = 2.0
                    
                    level_data = {
                        'activate_at': activate_at,
                        'move_sl_to': 'dynamic',
                        'trailing_distance': trailing_distance,
                        'description': descripciones_fijas[i]
                    }
                else:
                    move_sl_to_val = float(entry_dict['move_entry'].get())
                    level_data = {
                        'activate_at': activate_at,
                        'move_sl_to': move_sl_to_val,
                        'description': descripciones_fijas[i]
                    }
                
                levels.append(level_data)
            
            # Validar que los niveles estén en orden ascendente
            for i in range(1, len(levels)):
                if levels[i]['activate_at'] <= levels[i-1]['activate_at']:
                    messagebox.showerror("Error de Validación", 
                                       f"El nivel {i+1} debe activarse después del nivel {i}\n"
                                       f"Nivel {i}: {levels[i-1]['activate_at']}%\n"
                                       f"Nivel {i+1}: {levels[i]['activate_at']}%")
                    return
            
            # Guardar en configuración
            DEFAULT_CONFIG['trailing_hierarchical'] = {
                'enabled': hierarchical_enabled_var.get(),
                'levels': levels
            }
            
            guardar_configuracion()
            
            logger.log("✅ Configuración de trailing jerárquico guardada", "INFO", "success")
            config_window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", 
                               f"Dato inválido: {str(e)}\n\n"
                               f"Los valores deben ser números (ej: 1.5, 2.0) para todos los campos editables.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    # Botones - CENTRADOS
    btn_frame = tk.Frame(main_frame, bg='#2c2c2c', pady=10)
    btn_frame.pack(fill='x', pady=(5, 0))
    
    # Contenedor para centrar botones
    btn_container = tk.Frame(btn_frame, bg='#2c2c2c')
    btn_container.pack(expand=True)
    
    btn_guardar = tk.Button(btn_container, text="GUARDAR", command=guardar_config_trailing,
                           bg='#1abc9c', fg='#000000', font=('Arial', 9),
                           width=10, height=1)
    btn_guardar.pack(side='left', padx=(0, 8))
    
    btn_cancelar = tk.Button(btn_container, text="CANCELAR", command=config_window.destroy,
                            bg='#e74c3c', fg='#ffffff', font=('Arial', 9),
                            width=10, height=1)
    btn_cancelar.pack(side='left', padx=(0, 8))
    
    btn_reset = tk.Button(btn_container, text="RESET", 
                          command=cargar_valores_por_defecto,
                          bg='#3498db', fg='#ffffff', font=('Arial', 9),
                          width=10, height=1)
    btn_reset.pack(side='left')
    
    # Centrar ventana
    config_window.update_idletasks()
    width = config_window.winfo_width()
    height = config_window.winfo_height()
    x = (config_window.winfo_screenwidth() // 2) - (width // 2)
    y = (config_window.winfo_screenheight() // 2) - (height // 2)
    config_window.geometry(f'{width}x{height}+{x}+{y}')

btn_config_estrategia_small = tk.Button(
    button_strategy_frame,
    text="Configurar Estrategia",
    command=abrir_config_estrategia,
    bg='#3498db',
    fg='#ffffff',
    font=('Arial', 9),
    width=20
)
btn_config_estrategia_small.pack(side='left', padx=(0, 10))

# NUEVO: Botón para configurar trailing jerárquico
btn_trailing_niveles = tk.Button(
    button_strategy_frame,
    text="Trailing Jerárquico",
    command=abrir_config_trailing_niveles,
    bg='#1abc9c',
    fg='#000000',
    font=('Arial', 9),
    width=18
)
btn_trailing_niveles.pack(side='left', padx=(0, 10))

btn_reset_small = tk.Button(
    button_strategy_frame,
    text="Reset Fábrica",
    command=reset_a_fabrica,
    bg='#f1c40f',
    fg='#000000',
    font=('Arial', 9),
    width=15
)
btn_reset_small.pack(side='left')

# BOTONERA COMPACTA CON PANEL DE ESTADO EN VIVO
control_panel_frame = tk.Frame(config_frame, bg='#2c2c2c')
control_panel_frame.grid(row=12, column=0, columnspan=6, sticky='ew', pady=(10,0))

buttons_frame = tk.Frame(control_panel_frame, bg='#2c2c2c')
buttons_frame.pack(side='left', fill='y', padx=(0, 20))

btn_row1 = tk.Frame(buttons_frame, bg='#2c2c2c')
btn_row1.pack(fill='x', pady=(0, 10))

btn_guardar = tk.Button(btn_row1, text="Guardar Configuración",
                        command=guardar_configuracion,
                        bg='#3498db', fg='#ffffff', font=('Arial', 9),
                        width=20, height=1)
btn_guardar.pack(side='left', padx=(0, 10))

btn_cargar = tk.Button(btn_row1, text="Cargar Configuración",
                       command=cargar_configuracion,
                       bg='#2ecc71', fg='#000000', font=('Arial', 9),
                       width=20, height=1)
btn_cargar.pack(side='left')

btn_row2 = tk.Frame(buttons_frame, bg='#2c2c2c')
btn_row2.pack(fill='x', pady=(0, 10))

btn_reporte = tk.Button(btn_row2, text="Generar Reporte",
                        command=generar_reporte_diario,
                        bg='#f39c12', fg='#000000', font=('Arial', 9),
                        width=20, height=1)
btn_reporte.pack(side='left', padx=(0, 10))

btn_carpeta = tk.Button(btn_row2, text="Carpeta Reportes",
                        command=seleccionar_carpeta_reportes,
                        bg='#9b59b6', fg='#ffffff', font=('Arial', 9),
                        width=20, height=1)
btn_carpeta.pack(side='left')

btn_row3 = tk.Frame(buttons_frame, bg='#2c2c2c')
btn_row3.pack(fill='x', pady=(0, 5))

btn_iniciar = tk.Button(btn_row3, text="INICIAR BOT",
                        command=lambda: start_bot_thread(),
                        bg='#1e8449', fg='#ffffff', font=('Arial', 9, 'bold'),
                        width=20, height=1)
btn_iniciar.pack(side='left', padx=(0, 10))

btn_detener = tk.Button(btn_row3, text="DETENER BOT",
                        command=lambda: stop_bot(),
                        bg='#c0392b', fg='#ffffff', font=('Arial', 9, 'bold'),
                        width=20, height=1)
btn_detener.pack(side='left')

# PANEL DE ESTADO EN VIVO
panel_main_frame = tk.LabelFrame(control_panel_frame, text="📊 PANEL EN VIVO", 
                                font=('Arial', 9, 'bold'),
                                bg='#1a1a1a', fg='#2ecc71',
                                padx=12, pady=12, relief='groove', bd=2)
panel_main_frame.pack(side='right', fill='both', expand=True)

panel_header = tk.Frame(panel_main_frame, bg='#1a1a1a')
panel_header.pack(fill='x', pady=(0, 10))

title_label = tk.Label(panel_header, text="ESTADO", 
                      font=('Arial', 9, 'bold'),
                      bg='#1a1a1a', fg='#2ecc71')
title_label.pack(side='left')

led_canvas = tk.Canvas(panel_header, width=20, height=20, 
                      bg='#1a1a1a', highlightthickness=0)
led_canvas.pack(side='right', padx=(5, 0))
led = led_canvas.create_oval(2, 2, 18, 18, fill='#555555', outline='#888888', width=2)
led_status = "off"

status_vars = {
    'sesion': tk.StringVar(value="00:00:00"),
    'ciclo': tk.StringVar(value="#0"),
    'roi_diario': tk.StringVar(value="+0.00%"),
    'pnl_diario': tk.StringVar(value="+0.00 USDT"),
    'señales': tk.StringVar(value="0"),
    'activos': tk.StringVar(value="0/2"),
    'exitos': tk.StringVar(value="0"),
    'fallos': tk.StringVar(value="0"),
    'ultima_señal': tk.StringVar(value="Esperando..."),
    'roi_actual': tk.StringVar(value="+0.00%"),
    'errores': tk.StringVar(value="0"),
    # NUEVO: Estado Focus Mode
    'focus_mode': tk.StringVar(value="NORMAL")
}

panel_grid = tk.Frame(panel_main_frame, bg='#1a1a1a')
panel_grid.pack(fill='both', expand=True)

row1 = tk.Frame(panel_grid, bg='#1a1a1a')
row1.pack(fill='x', pady=2)

tk.Label(row1, text="🕐 Sesión:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row1, textvariable=status_vars['sesion'], bg='#1a1a1a', fg='#ffffff',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 15))

tk.Label(row1, text="🔄 Ciclo:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row1, textvariable=status_vars['ciclo'], bg='#1a1a1a', fg='#ffffff',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 0))

row2 = tk.Frame(panel_grid, bg='#1a1a1a')
row2.pack(fill='x', pady=2)

tk.Label(row2, text="📈 ROI:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row2, textvariable=status_vars['roi_diario'], bg='#1a1a1a', fg='#2ecc71',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 15))

tk.Label(row2, text="💰 P&L:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row2, textvariable=status_vars['pnl_diario'], bg='#1a1a1a', fg='#2ecc71',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 0))

row3 = tk.Frame(panel_grid, bg='#1a1a1a')
row3.pack(fill='x', pady=2)

tk.Label(row3, text="🎯 Señales:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row3, textvariable=status_vars['señales'], bg='#1a1a1a', fg='#3498db',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 15))

tk.Label(row3, text="💼 Activos:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row3, textvariable=status_vars['activos'], bg='#1a1a1a', fg='#3498db',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 0))

row4 = tk.Frame(panel_grid, bg='#1a1a1a')
row4.pack(fill='x', pady=2)

tk.Label(row4, text="✅ Éxitos:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row4, textvariable=status_vars['exitos'], bg='#1a1a1a', fg='#2ecc71',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 15))

tk.Label(row4, text="❌ Fallos:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')
tk.Label(row4, textvariable=status_vars['fallos'], bg='#1a1a1a', fg='#e74c3c',
        font=('Consolas', 8, 'bold')).pack(side='left', padx=(5, 0))

separator = tk.Frame(panel_grid, height=1, bg='#333333')
separator.pack(fill='x', pady=8)

signal_frame = tk.Frame(panel_grid, bg='#1a1a1a')
signal_frame.pack(fill='x', pady=(0, 5))

tk.Label(signal_frame, text="📡 Última:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left', anchor='n')

signal_text = tk.Label(signal_frame, textvariable=status_vars['ultima_señal'],
                      bg='#1a1a1a', fg='#3498db', font=('Consolas', 8),
                      wraplength=180, justify='left', anchor='w')
signal_text.pack(side='left', padx=(5, 0), fill='x', expand=True)

roi_frame = tk.Frame(panel_grid, bg='#1a1a1a')
roi_frame.pack(fill='x', pady=(5, 0))

tk.Label(roi_frame, text="📊 ROI Act:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')

roi_value = tk.Label(roi_frame, textvariable=status_vars['roi_actual'],
                    bg='#1a1a1a', fg='#2ecc71', font=('Consolas', 9, 'bold'))
roi_value.pack(side='left', padx=(5, 0))

# NUEVO: Fila para Focus Mode
focus_frame = tk.Frame(panel_grid, bg='#1a1a1a')
focus_frame.pack(fill='x', pady=(5, 0))

tk.Label(focus_frame, text="🎯 Modo:", bg='#1a1a1a', fg='#aaaaaa', 
        font=('Arial', 8)).pack(side='left')

focus_value = tk.Label(focus_frame, textvariable=status_vars['focus_mode'],
                      bg='#1a1a1a', fg='#f39c12', font=('Consolas', 8, 'bold'))
focus_value.pack(side='left', padx=(5, 0))

def set_led_status(status, blink=False):
    global led_status
    
    colors = {
        'connected': '#2ecc71',
        'error': '#e74c3c',
        'warning': '#f39c12',
        'off': '#555555'
    }
    
    color = colors.get(status, '#555555')
    if led_canvas and led:
        led_canvas.itemconfig(led, fill=color, outline=color)
    
    if blink and led_canvas:
        for _ in range(2):
            led_canvas.itemconfig(led, fill='#ffffff')
            root.update()
            time.sleep(0.1)
            led_canvas.itemconfig(led, fill=color)
            root.update()
            time.sleep(0.1)
    
    led_status = status

def register_error(error_msg=None):
    if not hasattr(register_error, 'count'):
        register_error.count = 0
    
    register_error.count += 1
    status_vars['errores'].set(str(register_error.count))
    status_vars['fallos'].set(str(register_error.count))
    
    set_led_status('error', blink=True)
    
    if bot_running:
        root.after(5000, lambda: check_and_reset_led())

def check_and_reset_led():
    if bot_running and led_status != 'error':
        set_led_status('connected')

def set_connected():
    set_led_status('connected')
    if hasattr(register_error, 'count'):
        register_error.count = 0
        status_vars['errores'].set("0")

def set_warning():
    set_led_status('warning')

def actualizar_panel():
    if bot_running:
        if 'start_time' in actualizar_panel.__dict__:
            elapsed = time.time() - actualizar_panel.start_time
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            status_vars['sesion'].set(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        
        try:
            max_trades = int(max_trades_entry.get().strip())
            active_count = len(active_trades)
            status_vars['activos'].set(f"{active_count}/{max_trades}")
            
            # NUEVO: Actualizar Focus Mode status
            if active_count >= max_trades:
                status_vars['focus_mode'].set("🔴 FOCUS")
                focus_value.config(fg='#e74c3c')
            else:
                status_vars['focus_mode'].set("🟢 NORMAL")
                focus_value.config(fg='#2ecc71')
        except:
            status_vars['activos'].set(f"{len(active_trades)}/1")
        
        if trade_history:
            pnl_total = sum(t.get('pnl_usdt', 0) for t in trade_history)
            capital_total = float(capital_entry.get()) * len(trade_history) if trade_history else 1
            roi_pct = (pnl_total / capital_total) * 100 if capital_total > 0 else 0
            
            signo = "+" if pnl_total >= 0 else ""
            status_vars['roi_diario'].set(f"{signo}{roi_pct:.2f}%")
            status_vars['pnl_diario'].set(f"{signo}{abs(pnl_total):.2f} USDT")
            
            exitos = sum(1 for t in trade_history if t.get('pnl_usdt', 0) > 0)
            fallos = sum(1 for t in trade_history if t.get('pnl_usdt', 0) < 0)
            status_vars['exitos'].set(str(exitos))
            if not hasattr(register_error, 'count') or register_error.count == 0:
                status_vars['fallos'].set(str(fallos))
        
        if hasattr(bot_cycle_thread, 'ciclo_count'):
            status_vars['ciclo'].set(f"#{bot_cycle_thread.ciclo_count}")
        
        if hasattr(detect_breakout_simple, 'signals_count'):
            status_vars['señales'].set(str(detect_breakout_simple.signals_count))
        
        if active_trades and client:
            total_roi = 0
            count = 0
            for symbol, trade in list(active_trades.items()):
                try:
                    positions = client.futures_position_information(symbol=symbol)
                    if positions:
                        position_info = positions[0]
                        entry_price = trade['entry_price']
                        current_price = float(position_info.get('markPrice', entry_price))
                        position_qty = abs(float(position_info.get('positionAmt', 0)))
                        leverage = trade.get('leverage', float(leverage_entry.get()))
                        
                        if position_qty > 0 and entry_price > 0:
                            capital = (position_qty * entry_price) / leverage if leverage > 0 else 1
                            
                            if trade['direction'] == "LONG":
                                pnl = (current_price - entry_price) * position_qty
                            else:
                                pnl = (entry_price - current_price) * position_qty
                            
                            roi = (pnl / capital) * 100 if capital > 0 else 0
                            total_roi += roi
                            count += 1
                except:
                    continue
            
            if count > 0:
                avg_roi = total_roi / count
                signo = "+" if avg_roi >= 0 else ""
                status_vars['roi_actual'].set(f"{signo}{avg_roi:.2f}%")
            else:
                status_vars['roi_actual'].set("+0.00%")
    
    root.after(1000, actualizar_panel)

root.after(1000, actualizar_panel)

# COLUMNA DERECHA: CONSOLA Y FILTROS
right_frame = tk.Frame(main_frame, bg="#1e1e1e", width=500)
right_frame.pack(side='right', fill='both', expand=True)

filters_frame = tk.LabelFrame(right_frame, text="FILTROS DE LOGS", font=('Arial', 9, 'bold'),
                             bg='#2c2c2c', fg='#3498db', padx=10, pady=8)
filters_frame.pack(fill='x', pady=(0, 5))

show_error_var = tk.IntVar(value=1)
show_trade_var = tk.IntVar(value=1)
show_info_var = tk.IntVar(value=0)
show_debug_var = tk.IntVar(value=0)
show_strategy_var = tk.IntVar(value=0)
show_orders_var = tk.IntVar(value=1)
show_momentum_var = tk.IntVar(value=1)

def update_error_filter():
    if logger:
        logger.set_filter('ERROR', bool(show_error_var.get()))

def update_trade_filter():
    if logger:
        logger.set_filter('TRADE', bool(show_trade_var.get()))

def update_info_filter():
    if logger:
        logger.set_filter('INFO', bool(show_info_var.get()))

def update_debug_filter():
    if logger:
        logger.set_filter('DEBUG', bool(show_debug_var.get()))

def update_strategy_filter():
    if logger:
        logger.set_filter('ESTRATEGIA', bool(show_strategy_var.get()))

def update_orders_filter():
    if logger:
        logger.set_filter('ORDERS', bool(show_orders_var.get()))

def update_momentum_filter():
    if logger:
        logger.set_filter('MOMENTUM', bool(show_momentum_var.get()))

checkbox_horizontal_frame = tk.Frame(filters_frame, bg='#2c2c2c')
checkbox_horizontal_frame.pack(fill='x', pady=5)

tk.Checkbutton(checkbox_horizontal_frame, text="ERROR", variable=show_error_var,
               command=update_error_filter,
               bg='#2c2c2c', fg='#e74c3c', selectcolor='#2c2c2c',
               font=('Arial', 9)).pack(side='left', padx=(0, 6))

tk.Checkbutton(checkbox_horizontal_frame, text="TRADE", variable=show_trade_var,
               command=update_trade_filter,
               bg='#2c2c2c', fg='#3498db', selectcolor='#2c2c2c',
               font=('Arial', 9)).pack(side='left', padx=(0, 6))

tk.Checkbutton(checkbox_horizontal_frame, text="INFO", variable=show_info_var,
               command=update_info_filter,
               bg='#2c2c2c', fg='#f0f0f0', selectcolor='#2c2c2c',
               font=('Arial', 9)).pack(side='left', padx=(0, 6))

tk.Checkbutton(checkbox_horizontal_frame, text="DEBUG", variable=show_debug_var,
               command=update_debug_filter,
               bg='#2c2c2c', fg='#aaaaaa', selectcolor='#2c2c2c',
               font=('Arial', 9)).pack(side='left', padx=(0, 6))

tk.Checkbutton(checkbox_horizontal_frame, text="ESTRATEGIA", variable=show_strategy_var,
               command=update_strategy_filter,
               bg='#2c2c2c', fg='#2ecc71', selectcolor='#2c2c2c',
               font=('Arial', 9)).pack(side='left', padx=(0, 6))

tk.Checkbutton(checkbox_horizontal_frame, text="ORDERS", variable=show_orders_var,
               command=update_orders_filter,
               bg='#2c2c2c', fg='#f39c12', selectcolor='#2c2c2c',
               font=('Arial', 9)).pack(side='left', padx=(0, 6))

tk.Checkbutton(checkbox_horizontal_frame, text="MOMENTUM", variable=show_momentum_var,
               command=update_momentum_filter,
               bg='#2c2c2c', fg='#e67e22', selectcolor='#2c2c2c',
               font=('Arial', 9)).pack(side='left', padx=(0, 6))

consola_frame = tk.LabelFrame(right_frame, text="MONITOR", font=('Arial', 10, 'bold'),
                             bg='#2c2c2c', fg='#f0f0f0', padx=10, pady=10)
consola_frame.pack(fill='both', expand=True)

log_text = scrolledtext.ScrolledText(consola_frame, height=15, state='disabled',
                                    bg='#1a1a1a', fg='#f0f0f0', font=('Consolas', 9))
log_text.pack(fill='both', expand=True)

log_text.tag_config('timestamp', foreground='#aaaaaa')
log_text.tag_config('info', foreground='#f0f0f0')
log_text.tag_config('success', foreground='#2ecc71')
log_text.tag_config('error', foreground='#e74c3c')
log_text.tag_config('warning', foreground='#f39c12')
log_text.tag_config('trade', foreground='#3498db')
log_text.tag_config('break_even', foreground='#9b59b6')
log_text.tag_config('profit', foreground='#2ecc71')
log_text.tag_config('rotator', foreground='#f39c12')
log_text.tag_config('trailing', foreground='#1abc9c')
log_text.tag_config('timeframe', foreground='#f1c40f')
log_text.tag_config('report', foreground='#9b59b6')
log_text.tag_config('strategy', foreground='#3498db')
log_text.tag_config('momentum', foreground='#e67e22')
log_text.tag_config('focus', foreground='#f39c12')  # NUEVO: Color para logs de Focus Mode

logger = LoggerProfesional(log_text)

# ============================================================
# FUNCIONES AUXILIARES DE BINANCE (SYNC)
# ============================================================
def conectar_binance():
    global client
    if client is None:
        api_key = api_key_entry.get()
        api_secret = api_secret_entry.get()
        if api_key and api_secret:
            try:
                if paper_var.get():
                    client = Client(api_key, api_secret, testnet=True)
                    client.futures_exchange_info()
                    logger.log("Conectado a Binance TESTNET", "INFO", "success")
                else:
                    client = Client(api_key, api_secret)
                    client.futures_exchange_info()
                    logger.log("Conectado a Binance REAL", "INFO", "success")
                set_connected()
                return True
            except Exception as e:
                logger.log(f"Error de conexión API: {e}", "ERROR", "error")
                register_error()
                client = None
                return False
        else:
            logger.log("Faltan API Key o Secret", "ERROR", "error")
            return False
    return client is not None

def get_symbol_price(symbol):
    try:
        return float(client.futures_symbol_ticker(symbol=symbol)['price'])
    except:
        return None

def get_open_positions_count():
    count = 0
    try:
        positions = client.futures_position_information()
        for p in positions:
            if float(p['positionAmt']) != 0:
                count += 1
    except:
        pass
    return count

def get_symbols_with_positions():
    active_symbols = set()
    try:
        positions = client.futures_position_information()
        for p in positions:
            if float(p['positionAmt']) != 0:
                active_symbols.add(p['symbol'])
    except Exception as e:
        logger.log(f"Error al obtener posiciones abiertas: {e}", "ERROR", "error")
    return active_symbols

def get_position_data(symbol):
    try:
        positions = client.futures_position_information(symbol=symbol)
        if positions:
            position = positions[0]
            position_qty = abs(float(position['positionAmt']))
            entry_price = float(position['entryPrice'])
            unrealized_pnl = float(position['unRealizedProfit'])
            return position_qty, entry_price, unrealized_pnl
    except:
        pass
    return 0, 0, 0

def get_leverage(symbol):
    try:
        leverage_data = client.futures_get_leverage(symbol=symbol)
        return int(leverage_data['leverage'])
    except:
        return int(leverage_entry.get())

def get_tick_size(symbol):
    try:
        exchange_info = client.futures_exchange_info()
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                for f in s['filters']:
                    if f['filterType'] == 'PRICE_FILTER':
                        return float(f['tickSize'])
        return 0.0001
    except:
        return 0.0001

def round_to_tick(price, tick):
    return round(price / tick) * tick

def registrar_trade_para_reporte(symbol, trade_type, entry_price, exit_price, roi_percent,
                                 pnl_usdt, estrategia, motivo, duracion_segundos):
    trade_data = {
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'symbol': symbol,
        'tipo': trade_type,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'roi_percent': roi_percent,
        'pnl_usdt': pnl_usdt,
        'estrategia': estrategia,
        'motivo': motivo,
        'duracion': duracion_segundos,
        'resultado': 'GANANCIA' if pnl_usdt > 0 else 'PERDIDA' if pnl_usdt < 0 else 'BREAKEVEN'
    }
    trade_history.append(trade_data)

# ============================================================
# FUNCIONES DE INDICADORES TÉCNICOS
# ============================================================
def calcular_ema(precios, periodo):
    if len(precios) < periodo:
        return None
    
    ema = [sum(precios[:periodo]) / periodo]
    multiplier = 2 / (periodo + 1)
    
    for i in range(periodo, len(precios)):
        ema_val = (precios[i] - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_val)
    
    return ema[-1]

def calcular_cci(precios_high, precios_low, precios_close, periodo=20):
    if len(precios_close) < periodo:
        return None
    
    tp = [(high + low + close) / 3 for high, low, close in zip(precios_high, precios_low, precios_close)]
    
    sma_tp = []
    for i in range(periodo-1, len(tp)):
        sma_tp.append(sum(tp[i-periodo+1:i+1]) / periodo)
    
    cci_values = []
    for i in range(len(sma_tp)):
        start_idx = i
        end_idx = i + periodo
        
        mean_dev = sum(abs(tp[start_idx:end_idx][j] - sma_tp[i]) for j in range(periodo)) / periodo
        
        if mean_dev == 0:
            cci_values.append(0)
        else:
            cci_val = (tp[end_idx-1] - sma_tp[i]) / (0.015 * mean_dev)
            cci_values.append(cci_val)
    
    return cci_values[-1] if cci_values else None

# ============================================================
# NUEVO: FUNCIÓN DE TRAILING JERÁRQUICO - CORREGIDA
# ============================================================
def apply_hierarchical_trailing(symbol, trade, current_roi, current_price):
    """
    Aplica trailing stop jerárquico por niveles - CORREGIDA
    """
    # Verificar si está activado
    hierarchical_config = DEFAULT_CONFIG['trailing_hierarchical']
    if not hierarchical_config.get('enabled', 0):
        return False  # Usar trailing simple
    
    levels = hierarchical_config.get('levels', [])
    if not levels:
        return False
    
    # Inicializar nivel actual si no existe
    if 'current_level' not in trade:
        trade['current_level'] = 0
        trade['levels_activated'] = []
    
    current_level = trade['current_level']
    
    # Si ya pasamos todos los niveles, usar trailing clásico
    if current_level >= len(levels):
        return False
    
    # Obtener nivel actual
    level = levels[current_level]
    activate_at = level['activate_at']
    
    # Verificar si alcanzamos el ROI para activar este nivel
    if current_roi >= activate_at and current_level not in trade['levels_activated']:
        leverage = trade.get('leverage', float(leverage_entry.get()))
        move_to = level['move_sl_to']
        
        if move_to == 'dynamic':
            # Trailing clásico
            trailing_distance = level.get('trailing_distance', 2.0)
            
            if trade['direction'] == "LONG":
                new_sl_price = current_price * (1 - (trailing_distance / leverage) / 100)
            else:
                new_sl_price = current_price * (1 + (trailing_distance / leverage) / 100)
            
            logger.log(f"{symbol}: 🏁 NIVEL {current_level+1} ACTIVADO - Trailing Dinámico (±{trailing_distance}%)", 
                      "TRADE", "trailing")
        else:
            # SL fijo en porcentaje específico
            new_sl_roi = float(move_to)
            entry_price = trade['entry_price']
            
            if trade['direction'] == "LONG":
                new_sl_price = entry_price * (1 + (new_sl_roi / leverage) / 100)
            else:
                new_sl_price = entry_price * (1 - (new_sl_roi / leverage) / 100)
            
            logger.log(f"{symbol}: 📈 NIVEL {current_level+1} ACTIVADO - SL movido a +{new_sl_roi}% ROI", 
                      "TRADE", "trailing")
        
        # Mover el SL
        try:
            tick_size = get_tick_size(symbol)
            formatted_sl_price = round_to_tick(new_sl_price, tick_size)
            formatted_sl_price = f"{formatted_sl_price:.8f}".rstrip('0').rstrip('.')
            
            # Cancelar SL anterior
            if trade.get('sl_id'):
                try:
                    client.futures_cancel_order(symbol=symbol, orderId=trade['sl_id'])
                    time.sleep(0.2)
                except:
                    pass
            
            # Colocar nuevo SL
            side_order = SIDE_SELL if trade['direction'] == "LONG" else SIDE_BUY
            order = client.futures_create_order(
                symbol=symbol,
                side=side_order,
                type="STOP_MARKET",
                closePosition=True,
                stopPrice=formatted_sl_price,
                timeInForce=TIME_IN_FORCE_GTC
            )
            
            trade['sl_id'] = order.get('orderId')
            trade['levels_activated'].append(current_level)
            trade['current_level'] = current_level + 1
            trade['trailing_activated'] = True
            
            # Si es trailing dinámico, guardar el precio máximo/mínimo
            if move_to == 'dynamic':
                if trade['direction'] == "LONG":
                    trade['highest_price'] = current_price
                else:
                    trade['lowest_price'] = current_price
            
            logger.log(f"{symbol}: ✅ SL movido a {formatted_sl_price} (Nivel {current_level+1})", 
                      "ORDERS", "success")
            return True
            
        except Exception as e:
            logger.log(f"Error al mover SL jerárquico: {e}", "ERROR", "error")
            return False
    
    # Si estamos en nivel dinámico (último nivel), actualizar trailing
    elif current_level == len(levels) and levels[-1].get('move_sl_to') == 'dynamic':
        # Actualizar precio máximo/mínimo
        if trade['direction'] == "LONG" and current_price > trade.get('highest_price', 0):
            trade['highest_price'] = current_price
        elif trade['direction'] == "SHORT" and current_price < trade.get('lowest_price', float('inf')):
            trade['lowest_price'] = current_price
        
        # Calcular nuevo SL para trailing dinámico
        trailing_distance = levels[-1].get('trailing_distance', 2.0)
        leverage = trade.get('leverage', float(leverage_entry.get()))
        
        if trade['direction'] == "LONG":
            new_sl_price = trade['highest_price'] * (1 - (trailing_distance / leverage) / 100)
        else:
            new_sl_price = trade['lowest_price'] * (1 + (trailing_distance / leverage) / 100)
        
        # Verificar si necesitamos mover el SL
        current_sl_price = 0
        try:
            if trade.get('sl_id'):
                orders = client.futures_get_open_orders(symbol=symbol)
                for order in orders:
                    if order['orderId'] == trade['sl_id']:
                        current_sl_price = float(order.get('stopPrice', 0))
                        break
        except:
            pass
        
        # Solo mover si hay una mejora significativa
        if trade['direction'] == "LONG" and new_sl_price > current_sl_price:
            try:
                tick_size = get_tick_size(symbol)
                formatted_sl_price = round_to_tick(new_sl_price, tick_size)
                formatted_sl_price = f"{formatted_sl_price:.8f}".rstrip('0').rstrip('.')
                
                # Cancelar SL anterior
                client.futures_cancel_order(symbol=symbol, orderId=trade['sl_id'])
                time.sleep(0.2)
                
                # Colocar nuevo SL
                side_order = SIDE_SELL if trade['direction'] == "LONG" else SIDE_BUY
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side_order,
                    type="STOP_MARKET",
                    closePosition=True,
                    stopPrice=formatted_sl_price,
                    timeInForce=TIME_IN_FORCE_GTC
                )
                
                trade['sl_id'] = order.get('orderId')
                logger.log(f"{symbol}: 🔼 Trailing dinámico actualizado: {formatted_sl_price}", 
                          "TRADE", "trailing")
                return True
                
            except Exception as e:
                pass
        elif trade['direction'] == "SHORT" and new_sl_price < current_sl_price:
            try:
                tick_size = get_tick_size(symbol)
                formatted_sl_price = round_to_tick(new_sl_price, tick_size)
                formatted_sl_price = f"{formatted_sl_price:.8f}".rstrip('0').rstrip('.')
                
                # Cancelar SL anterior
                client.futures_cancel_order(symbol=symbol, orderId=trade['sl_id'])
                time.sleep(0.2)
                
                # Colocar nuevo SL
                side_order = SIDE_SELL if trade['direction'] == "LONG" else SIDE_BUY
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side_order,
                    type="STOP_MARKET",
                    closePosition=True,
                    stopPrice=formatted_sl_price,
                    timeInForce=TIME_IN_FORCE_GTC
                )
                
                trade['sl_id'] = order.get('orderId')
                logger.log(f"{symbol}: 🔽 Trailing dinámico actualizado: {formatted_sl_price}", 
                          "TRADE", "trailing")
                return True
                
            except Exception as e:
                pass
    
    return False

# ============================================================
# SISTEMA ASYNC PARA ESCANEO PARALELO
# ============================================================
async_client_instance = None
async_semaphore = asyncio.Semaphore(15)  # Control de concurrencia

async def init_async_client():
    """Inicializa el cliente async con manejo de reconexión"""
    global async_client_instance
    if async_client_instance is None:
        try:
            api_key = api_key_entry.get()
            api_secret = api_secret_entry.get()
            testnet = bool(paper_var.get())
            async_client_instance = await AsyncClient.create(api_key, api_secret, testnet=testnet)
            logger.log("Cliente async inicializado correctamente", "INFO", "success")
        except Exception as e:
            logger.log(f"Error al inicializar cliente async: {e}", "ERROR", "error")
            async_client_instance = None
            raise
    return async_client_instance

async def fetch_klines_async(symbol, tf):
    """Fetch asíncrono con REINTENTOS INTELIGENTES - Sin timeouts"""
    max_retries = 3
    base_delay = 2  # segundos
    
    for attempt in range(max_retries):
        try:
            api_key = api_key_entry.get()
            api_secret = api_secret_entry.get()
            testnet = bool(paper_var.get())
            
            # Crear cliente NUEVO cada vez (más estable)
            client = await AsyncClient.create(api_key, api_secret, testnet=testnet)
            
            try:
                # 🛠️ MAPA CORREGIDO DE INTERVALOS
                interval_map = {
                    "1m": "1m",
                    "3m": "3m", 
                    "5m": "5m",
                    "15m": "15m",
                    "30m": "30m",
                    "1h": "1h",
                    "2h": "2h",
                    "4h": "4h",
                    "12h": "12h", 
                    "1d": "1d"
                }
                
                # Usar el intervalo mapeado o "1m" por defecto
                api_interval = interval_map.get(tf, "1m")
                
                # ⚡ TIMEOUT PROGRESIVO: Mayor en cada reintento
                timeout = 15.0 + (attempt * 5.0)  # 15s, 20s, 25s
                
                klines = await asyncio.wait_for(
                    client.futures_klines(symbol=symbol, interval=api_interval, limit=100),
                    timeout=timeout
                )
                
                # ✅ LOG SOLO SI FUE LENTO (>3s) o es el último intento
                if attempt > 0:
                    logger.log(f"[DEBUG] {symbol}: Éxito en intento {attempt+1}/{max_retries}", "DEBUG", "success")
                
                return klines
            finally:
                await client.close_connection()
                
        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                # ⏳ REINTENTAR con espera progresiva
                wait_time = base_delay * (attempt + 1)  # 2s, 4s, 6s
                logger.log(f"[DEBUG] {symbol}: Timeout. Reintento {attempt+2}/{max_retries} en {wait_time}s...", "DEBUG", "warning")
                await asyncio.sleep(wait_time)
            else:
                # ❌ AGOTÓ TODOS LOS REINTENTOS
                logger.log(f"Timeout en klines de {symbol} (agotados {max_retries} intentos)", "ERROR", "error")
                return None
        except Exception as e:
            error_msg = str(e)
            if "Event loop is closed" not in error_msg:
                if "code=-1120" in error_msg:
                    logger.log(f"Error de intervalo en {symbol}: {tf} -> {api_interval}", "ERROR", "error")
                else:
                    logger.log(f"Error async en {symbol}: {error_msg}", "ERROR", "error")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay)
            else:
                return None
    
    return None

def run_async_scan(symbols):
    """
    ÚNICA VERSIÓN CORREGIDA - Escaneo PARALELO estable
    """
    if not symbols:
        return []
    
    results = []
    
    # Configurar para Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    def process_single_symbol(symbol):
        """Procesa UNA moneda en su propio loop"""
        try:
            # Crear loop NUEVO para esta moneda
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Ejecutar la función async
            async def process():
                tf = timeframe_var.get()
                kl = await fetch_klines_async(symbol, tf)
                
                if not kl or len(kl) < 50:
                    # LOG CRÍTICO: Ver si falla aquí
                    logger.log(f"[DEBUG] {symbol}: Sin datos o <50 velas", "DEBUG", "warning")
                    return symbol, None, None
                
                closes = [float(k[4]) for k in kl]
                highs  = [float(k[2]) for k in kl]
                lows   = [float(k[3]) for k in kl]
                
                # LOG CRÍTICO: Ver si llegan datos
                logger.log(f"[DEBUG] {symbol}: Datos OK. Velas={len(closes)}, Close={closes[-1]:.8f}", "DEBUG", "info")
                
                signal, cci = detect_breakout_logic(symbol, closes, highs, lows)
                return symbol, signal, cci
            
            result = loop.run_until_complete(process())
            loop.close()
            return result
            
        except Exception as e:
            logger.log(f"[DEBUG] {symbol}: Error en process: {e}", "DEBUG", "error")
            return symbol, None, None
    
    # Ejecutar en paralelo
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {executor.submit(process_single_symbol, symbol): symbol 
                          for symbol in symbols}
        
        for future in concurrent.futures.as_completed(future_to_symbol):
            try:
                result = future.result(timeout=20)
                if result and result[1] is not None:  # Si tiene señal
                    results.append(result)
            except concurrent.futures.TimeoutError:
                symbol = future_to_symbol[future]
                logger.log(f"Timeout procesando {symbol}", "ERROR", "error")
            except Exception as e:
                symbol = future_to_symbol[future]
                logger.log(f"Error procesando {symbol}: {e}", "ERROR", "error")
    
    return results

# ============================================================
# FUNCIÓN CRÍTICA: COLOCACIÓN DE ÓRDENES - CORREGIDA
# ============================================================
def colocar_ordenes_simple(symbol, direction, entry_price, qty):
    global active_trades, last_signal_time
    sl_placed = False
    tp_placed = False
    sl_order_id = None
    tp_order_id = None
    
    try:
        logger.log(f"Colocando SL y TP fijos para {symbol}...", "ORDERS")
        
        try:
            client.futures_cancel_all_open_orders(symbol=symbol)
            time.sleep(0.2)
        except:
            pass
        
        position_qty = 0
        real_entry_price = entry_price
        max_wait_seconds = 5
        
        for attempt in range(max_wait_seconds):
            try:
                positions = client.futures_position_information(symbol=symbol)
                position_info = positions[0]
            except Exception as e:
                time.sleep(1.0)
                continue
            
            position_qty = abs(float(position_info['positionAmt']))
            if float(position_info['entryPrice']) != 0:
                real_entry_price = float(position_info['entryPrice'])
            
            if position_qty > 0 and real_entry_price > 0:
                break
            
            if attempt == max_wait_seconds - 1:
                logger.log(f"Posición {symbol} no aparece en Binance después de {max_wait_seconds}s. Cancelando.", "ERROR", "error")
                return False
            
            time.sleep(1.0)
        
        if position_qty <= 0:
            logger.log(f"Posición {symbol} se cerró durante el proceso de espera.", "ERROR", "error")
            return False
        
        tick_size = get_tick_size(symbol)
        leverage = get_leverage(symbol)
        
        # PRIMERO COLOCAR TP (más fácil, menos restricciones)
        initial_tp_roi = float(tp_entry.get())
        current_tp_roi = initial_tp_roi
        max_retries = 3
        increment_roi = 0.05
        
        for attempt in range(max_retries):
            tp_percent_price = (current_tp_roi / leverage) / 100
            
            if direction == "LONG":
                tp_price = real_entry_price * (1 + tp_percent_price)
            else:
                tp_price = real_entry_price * (1 - tp_percent_price)
            
            formatted_tp_price = round_to_tick(tp_price, tick_size)
            formatted_tp_price = f"{formatted_tp_price:.8f}".rstrip('0').rstrip('.')
            
            try:
                side_order = SIDE_SELL if direction == "LONG" else SIDE_BUY
                
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side_order,
                    type="TAKE_PROFIT_MARKET",
                    closePosition=True,
                    stopPrice=formatted_tp_price,
                    timeInForce=TIME_IN_FORCE_GTC
                )
                logger.log(f"TP fijo ({current_tp_roi:.2f}%) colocado en {symbol} @ {formatted_tp_price}", "ORDERS", "success")
                tp_placed = True
                tp_order_id = order.get('orderId')
                break
            except Exception as e:
                error_str = str(e)
                if "code=-2021" in error_str:
                    logger.log(f"Error -2021 (TP Trigger Inmediato) en {symbol}. Reduciendo TP a {current_tp_roi - increment_roi:.2f}%", "ORDERS", "warning")
                    current_tp_roi -= increment_roi
                    time.sleep(0.5)
                else:
                    logger.log(f"Error CRÍTICO TP inesperado en {symbol}: {error_str}", "ERROR", "error")
                    break
        
        # LUEGO COLOCAR SL
        initial_sl_roi = float(sl_entry.get())
        current_sl_roi = initial_sl_roi
        
        for attempt in range(max_retries):
            sl_percent_price = (current_sl_roi / leverage) / 100
            
            if direction == "LONG":
                sl_price = real_entry_price * (1 - sl_percent_price)
            else:
                sl_price = real_entry_price * (1 + sl_percent_price)
            
            formatted_sl_price = round_to_tick(sl_price, tick_size)
            formatted_sl_price = f"{formatted_sl_price:.8f}".rstrip('0').rstrip('.')
            
            try:
                side_order = SIDE_SELL if direction == "LONG" else SIDE_BUY
                
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side_order,
                    type="STOP_MARKET",
                    closePosition=True,
                    stopPrice=formatted_sl_price,
                    timeInForce=TIME_IN_FORCE_GTC
                )
                logger.log(f"SL inicial ({current_sl_roi:.2f}%) colocado en {symbol} @ {formatted_sl_price}", "ORDERS", "success")
                sl_placed = True
                sl_order_id = order.get('orderId')
                break
            except Exception as e:
                error_str = str(e)
                if "code=-2021" in error_str:
                    logger.log(f"Error -2021 (SL Trigger Inmediato) en {symbol}. Aumentando SL a {current_sl_roi + increment_roi:.2f}%", "ORDERS", "warning")
                    current_sl_roi += increment_roi
                    time.sleep(0.5)
                else:
                    logger.log(f"Error CRÍTICO SL inesperado en {symbol}: {error_str}", "ERROR", "error")
                    break
        
        # VERIFICAR QUE AMBOS SE COLOCARON
        if not tp_placed and not sl_placed:
            logger.log(f"Fallo al colocar AMBAS órdenes en {symbol}. ¡CERRANDO POSICIÓN DE EMERGENCIA!", "ERROR", "error")
            try:
                side_close = SIDE_SELL if direction == "LONG" else SIDE_BUY
                client.futures_create_order(
                    symbol=symbol,
                    side=side_close,
                    type="MARKET",
                    quantity=position_qty
                )
                logger.log(f"Posición {symbol} CERRADA por EMERGENCIA.", "ERROR", "error")
            except Exception as close_e:
                logger.log(f"ERROR CRÍTICO: No se pudo cerrar la posición de emergencia: {close_e}", "ERROR", "error")
            return False
        elif not sl_placed:
            logger.log(f"ADVERTENCIA: SL no se pudo colocar en {symbol}, pero TP sí.", "ERROR", "warning")
        elif not tp_placed:
            logger.log(f"ADVERTENCIA: TP no se pudo colocar en {symbol}, pero SL sí.", "ERROR", "warning")
        
        if position_qty > 0:
            active_trades[symbol] = {
                'entry_price': real_entry_price,
                'direction': direction,
                'sl_id': sl_order_id,
                'tp_id': tp_order_id,
                'qty': position_qty,
                'initial_sl_roi': initial_sl_roi,
                'leverage': leverage,
                'max_profit_price': real_entry_price,
                'break_even_reached': False,
                'momentum_loss_evaluated': False,
                'momentum_candle_count': 0,
                'momentum_max_roi': 0,
                'open_time': time.time(),
                'current_level': 0,  # NUEVO: Inicializar nivel para trailing jerárquico
                'levels_activated': [],  # NUEVO: Niveles ya activados
                'trailing_activated': False,  # NUEVO: Para trailing dinámico
            }
            
            logger.log(f"Órdenes colocadas. Posición {symbol} ACTIVA.", "ORDERS", "success")
            return True
        else:
            logger.log(f"{symbol} cerrado en el proceso de colocación de SL/TP.", "TRADE", "profit")
            return False
    
    except Exception as e:
        logger.log(f"Error general en colocación: {str(e)}", "ERROR", "error")
        if symbol in get_symbols_with_positions():
            logger.log(f"Error general. Cerrando {symbol} por seguridad.", "ERROR", "error")
            final_position_qty = 0
            positions = client.futures_position_information()
            for p in positions:
                if p['symbol'] == symbol:
                    final_position_qty = abs(float(p['positionAmt']))
                    break
            
            if final_position_qty > 0:
                side_close = SIDE_SELL if direction == "LONG" else SIDE_BUY
                client.futures_create_order(symbol=symbol, side=side_close, type="MARKET", quantity=final_position_qty)
                logger.log(f"Posición {symbol} CERRADA por EMERGENCIA.", "ERROR", "error")
            return False
        return False

# ============================================================
# FUNCIONES DE ANÁLISIS TÉCNICO Y ROTATOR
# ============================================================
def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    
    sma = sum(prices[:period]) / period
    ema_values = [sma]
    
    multiplier = 2 / (period + 1)
    
    for price in prices[period:]:
        ema = (price - ema_values[-1]) * multiplier + ema_values[-1]
        ema_values.append(ema)
    
    return ema_values[-1]

# ============================================================
# FUNCIÓN DE DETECCIÓN DE SEÑALES (LÓGICA PURA)
# ============================================================
def detect_breakout_logic(symbol, closes, highs, lows):
    """
    Lógica PURA de detección de señales (separada del fetch).
    VERSIÓN CON LOGS DE DIAGNÓSTICO.
    """
    # ===== LOG DE ENTRADA =====
    logger.log(f"[ESTRATEGIA] {symbol}: Iniciando análisis (velas={len(closes)})", "ESTRATEGIA", "info")
    
    if not closes or len(closes) < 50:
        logger.log(f"[ESTRATEGIA] {symbol}: ERROR - No hay datos suficientes (<50 velas)", "ESTRATEGIA", "error")
        return None, None
    
    current_price = closes[-1]
    
        # ===== LÓGICA ANTI-SWEEP =====
    sweep_long = True
    sweep_short = True
    
    if anti_sweep_var.get():
        lookback = 20
        recent_high = max(highs[-lookback-1:-1])
        recent_low  = min(lows[-lookback-1:-1])
        
        last_high  = highs[-1]
        last_low   = lows[-1]
        last_close = closes[-1]
        
        # ===== LÓGICA CON SENSIBILIDAD AJUSTABLE (NUEVO) =====
        try:
            sensibilidad = float(anti_sweep_sensibilidad_var.get()) / 100.0
        except:
            sensibilidad = 0.005  # Valor por defecto 0.5% si hay error
        
        # ===== LÓGICA CORREGIDA (FILTRO DE BLOQUEO REAL) =====
        # 1. Determinar si ocurrió un movimiento de "sweep" significativo
        sweep_long_detectado = last_low < (recent_low * (1 - sensibilidad))
        sweep_short_detectado = last_high > (recent_high * (1 + sensibilidad))
        
        # 2. Determinar si el cierre fue DÉBIL (peligro de continuación)
        #    Para LONG: Cierre débil = No logró recuperarse por encima del mínimo reciente
        #    Para SHORT: Cierre débil = No logró bajar por debajo del máximo reciente
        cierre_debil_long = last_close < recent_low
        cierre_debil_short = last_close > recent_high
        
        # 3. BLOQUEAR solo si: Hubo sweep Y cierre débil (señal peligrosa)
        #    Esto evita operar en una posible continuación de la trampa.
        sweep_long_peligroso = sweep_long_detectado and cierre_debil_long
        sweep_short_peligroso = sweep_short_detectado and cierre_debil_short
        
        # ===== FIN LÓGICA CORREGIDA =====
        
        # ===== LOG ANTI-SWEEP =====
        logger.log(f"[ESTRATEGIA] {symbol}: Anti-Sweep | LH={last_high:.8f}, RH={recent_high:.8f}, LL={last_low:.8f}, RL={recent_low:.8f}", "ESTRATEGIA", "debug")
        logger.log(f"[ESTRATEGIA] {symbol}: Anti-Sweep | SweepDect(L={sweep_long_detectado}, S={sweep_short_detectado})", "ESTRATEGIA", "debug")
        logger.log(f"[ESTRATEGIA] {symbol}: Anti-Sweep | CierreDebil(L={cierre_debil_long}, S={cierre_debil_short})", "ESTRATEGIA", "debug")
        logger.log(f"[ESTRATEGIA] {symbol}: Anti-Sweep | BLOQUEAR(L={sweep_long_peligroso}, S={sweep_short_peligroso}, Sens={sensibilidad*100:.2f}%)", "ESTRATEGIA", "debug")
    
    # ===== LÓGICA EMA =====
    use_ema = use_ema_var.get()
    use_cci = use_cci_var.get()
    
    ema_signal = None
    cci_trigger = False
    cci_value = None
    
    if use_ema:
        ema_fast = calcular_ema(closes, int(DEFAULT_CONFIG['ema_fast_entry']))
        ema_slow = calcular_ema(closes, int(DEFAULT_CONFIG['ema_slow_entry']))
        
        # ===== LOG EMA =====
        logger.log(f"[ESTRATEGIA] {symbol}: EMA | Fast={ema_fast:.8f}, Slow={ema_slow:.8f}", "ESTRATEGIA", "debug")
        
        if ema_fast and ema_slow:
            if ema_fast > ema_slow and current_price > ema_fast:
                ema_signal = "LONG"
            elif ema_fast < ema_slow and current_price < ema_fast:
                ema_signal = "SHORT"
    
    # ===== LÓGICA CCI =====
    if use_cci and ema_signal:
        cci_period = int(DEFAULT_CONFIG['cci_period_entry'])
        cci_upper = int(DEFAULT_CONFIG['cci_upper_entry'])
        cci_lower = int(DEFAULT_CONFIG['cci_lower_entry'])
        
        cci_current = calcular_cci(highs, lows, closes, cci_period)
        cci_prev = calcular_cci(highs[:-1], lows[:-1], closes[:-1], cci_period) if len(closes) > 1 else 0
        
        cci_value = cci_current
        
        # ===== LOG CCI =====
        logger.log(f"[ESTRATEGIA] {symbol}: CCI | Actual={cci_current:.2f}, Anterior={cci_prev:.2f}, Límites[{cci_lower},{cci_upper}]", "ESTRATEGIA", "debug")
        
        if ema_signal == "LONG" and cci_prev <= cci_lower and cci_current > cci_lower:
            cci_trigger = True
            logger.log(f"[ESTRATEGIA] {symbol}: CCI TRIGGER LONG (cruce al alza)", "ESTRATEGIA", "debug")
        elif ema_signal == "SHORT" and cci_prev >= cci_upper and cci_current < cci_upper:
            cci_trigger = True
            logger.log(f"[ESTRATEGIA] {symbol}: CCI TRIGGER SHORT (cruce a la baja)", "ESTRATEGIA", "debug")
    
    # ===== DECISIÓN FINAL =====
    final_signal = None
    
    if use_ema and not use_cci:
        final_signal = ema_signal
    elif use_ema and use_cci and ema_signal and cci_trigger:
        final_signal = ema_signal
    
    # ===== LOG DE DECISIÓN PRE-ANTI-SWEEP =====
    if ema_signal:
        logger.log(f"[ESTRATEGIA] {symbol}: Señal EMA={ema_signal}, CCI Trigger={cci_trigger}, Señal Final={final_signal}", "ESTRATEGIA", "info")
    
    # ===== FILTRO ANTI-SWEEP FINAL (¡VERSIÓN CORREGIDA!) =====
    if anti_sweep_var.get():
        # ¡AHORA BLOQUEAMOS SI ES PELIGROSO! (No al revés)
        if final_signal == "LONG" and sweep_long_peligroso:
            logger.log(f"[ESTRATEGIA] {symbol}: ❌ SEÑAL LONG BLOQUEADA - Anti-Sweep detectó Sweep Bajista PELIGROSO", "ESTRATEGIA", "warning")
            return None, None
        if final_signal == "SHORT" and sweep_short_peligroso:
            logger.log(f"[ESTRATEGIA] {symbol}: ❌ SEÑAL SHORT BLOQUEADA - Anti-Sweep detectó Sweep Alcista PELIGROSO", "ESTRATEGIA", "warning")
            return None, None
    
    # ===== RESULTADO =====
    if final_signal:
        logger.log(f"[ESTRATEGIA] {symbol}: 🎯 SEÑAL {final_signal} CONFIRMADA (Price={current_price:.8f}, CCI={cci_value:.2f})", "ESTRATEGIA", "trade")
        return final_signal, cci_value
    
    logger.log(f"[ESTRATEGIA] {symbol}: Sin señal válida", "ESTRATEGIA", "debug")
    return None, None

# ============================================================
# DETECCIÓN DE SEÑALES (AHORA USA ASYNC)
# ============================================================
def detect_breakout_simple(symbol):
    """
    VERSIÓN MODIFICADA: Ahora solo es un wrapper que verifica condiciones básicas.
    La lógica real está en detect_breakout_logic() y el escaneo async.
    """
    if symbol in symbols_with_positions:
        return None, None

    try:
        max_trades = int(max_trades_entry.get().strip())
        if len(symbols_with_positions) >= max_trades:
            return None, None
    except ValueError:
        logger.log("ERROR: Máx. Trades inválido", "ERROR", "error")
        return None, None

    # Esta función ahora se llama desde el escaneo async
    # Mantenemos la función por compatibilidad pero la lógica real está en otro lugar
    return None, None

# ============================================================
# FUNCIÓN DE EJECUCIÓN DEL TRADE (SIN CAMBIOS)
# ============================================================
def open_trade_simple(symbol, direction, cci_signal=None):
    max_trades = int(max_trades_entry.get().strip())
    if len(symbols_with_positions) >= max_trades:
        logger.log(f"Límite de trades ({max_trades}) alcanzado. Ignorando {symbol}.", "INFO", "warning")
        return False
    
    leverage_value = int(leverage_entry.get().strip())
    try:
        client.futures_change_leverage(symbol=symbol, leverage=leverage_value)
    except Exception as e:
        logger.log(f"Error al ajustar leverage en {symbol}: {e}", "ERROR", "error")
    
    capital = float(capital_entry.get().strip())
    leverage = leverage_value
    
    try:
        price = get_symbol_price(symbol)
    except:
        logger.log(f"No se pudo obtener el precio de {symbol}.", "ERROR", "error")
        return False
    
    if price is None or price <= 0:
        logger.log(f"Precio inválido para {symbol}.", "ERROR", "error")
        return False
    
    qty = (capital * leverage) / price
    
    try:
        exchange_info = client.futures_exchange_info()
        step_size = 0.001
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                for f in s['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        step_size = float(f['stepSize'])
                        break
                break
        qty = math.floor(qty / step_size) * step_size
        qty = float(f"{qty:.8f}".rstrip('0').rstrip('.'))
    except Exception as e:
        logger.log(f"Error al redondear cantidad en {symbol}: {e}", "ERROR", "error")
        return False
    
    if qty <= 0:
        logger.log(f"Cantidad calculada ({qty}) inválida. Revisar capital/precio.", "INFO", "warning")
        return False
    
    side = SIDE_BUY if direction == "LONG" else SIDE_SELL
    try:
        client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=qty
        )
        
        time.sleep(2.0)
        
        positions = client.futures_position_information()
        entry_price = price
        real_qty = qty
        for p in positions:
            if p['symbol'] == symbol:
                if 'entryPrice' in p and float(p['entryPrice']) != 0:
                    entry_price = float(p['entryPrice'])
                real_qty = abs(float(p['positionAmt']))
                break
        
        if real_qty == 0:
            logger.log(f"Posición {symbol} falló al abrir (Cantidad real 0).", "ERROR", "error")
            return False
        
        tp_percent = float(tp_entry.get())
        sl_percent = float(sl_entry.get())
        leverage = leverage_value
        
        if direction == "LONG":
            tp_price = entry_price * (1 + (tp_percent / leverage) / 100)
            sl_price = entry_price * (1 - (sl_percent / leverage) / 100)
        else:
            tp_price = entry_price * (1 - (tp_percent / leverage) / 100)
            sl_price = entry_price * (1 + (sl_percent / leverage) / 100)
        
        logger.log_separator(f"POSICIÓN {direction} ABIERTA - {symbol}", "TRADE")
        logger.log(f"Par: {symbol}", "TRADE")
        logger.log(f"Dirección: {direction}", "TRADE")
        logger.log(f"Entrada: {entry_price:.8f}", "TRADE")
        logger.log(f"TP: {tp_price:.8f} ({tp_percent}%)", "TRADE", "success")
        logger.log(f"SL: {sl_price:.8f} ({sl_percent}%)", "TRADE", "error")
        if cci_signal:
            logger.log(f"CCI Signal: {cci_signal:.0f}", "TRADE")
        
        momentum_active = "SI" if momentum_loss_var.get() else "NO"
        anti_sweep_active = "SI" if anti_sweep_var.get() else "NO"
        logger.log(f"⚡ Momentum Loss: {momentum_active}", "TRADE")
        logger.log(f"🛡️ Anti-Sweep: {anti_sweep_active}", "TRADE")
        
        # NUEVO: Mostrar si trailing jerárquico está activado
        hierarchical_enabled = DEFAULT_CONFIG['trailing_hierarchical']['enabled']
        trailing_mode = "JERÁRQUICO" if hierarchical_enabled else "CLÁSICO"
        logger.log(f"📊 Trailing: {trailing_mode}", "TRADE", "trailing")
        
        # NUEVO: Mostrar niveles configurados si está activado
        if hierarchical_enabled:
            levels = DEFAULT_CONFIG['trailing_hierarchical']['levels']
            logger.log(f"📈 Niveles configurados:", "TRADE", "trailing")
            for i, level in enumerate(levels, 1):
                if level['move_sl_to'] == 'dynamic':
                    logger.log(f"  Nivel {i}: +{level['activate_at']}% → Trailing ±{level.get('trailing_distance', 2.0)}%", "TRADE", "trailing")
                else:
                    logger.log(f"  Nivel {i}: +{level['activate_at']}% → SL a +{level['move_sl_to']}%", "TRADE", "trailing")
        
        logger.log_separator("", "TRADE")
        
        success = colocar_ordenes_simple(symbol, direction, entry_price, real_qty)
        
        if success:
            last_signal_time[symbol] = time.time()
            symbols_with_positions.add(symbol)
            
            active_trades[symbol]['open_time'] = time.time()
            active_trades[symbol]['cci_signal'] = cci_signal
            
            active_trades[symbol]['momentum_loss_evaluated'] = False
            active_trades[symbol]['momentum_candle_count'] = 0
            active_trades[symbol]['momentum_max_roi'] = 0
            active_trades[symbol]['momentum_last_candle_time'] = time.time()
            
            tp_pct = float(tp_entry.get())
            sl_pct = float(sl_entry.get())
            logger.log(f"Ratio TP/SL: {tp_pct/sl_pct:.1f}:1", "TRADE", "trade")
            return success
    
    except Exception as e:
        logger.log(f"Error abriendo trade: {str(e)}", "ERROR", "error")
        return False
    return False

# ============================================================
# FUNCIÓN DE MOMENTUM LOSS (CORREGIDA - Cuenta velas REALES)
# ============================================================
def check_momentum_loss(symbol, trade, current_price, current_roi):
    if not momentum_loss_var.get():
        return False
    
    if trade.get('momentum_loss_evaluated', False):
        return False
    
    momentum_threshold = float(DEFAULT_CONFIG['momentum_loss_threshold_entry'])
    momentum_candles = int(DEFAULT_CONFIG['momentum_loss_candles_entry'])
    
    tf = timeframe_var.get()
    tf_minutes = int(tf.replace('m', ''))
    seconds_per_candle = tf_minutes * 60
    
    current_time = time.time()
    if 'momentum_last_candle_time' not in trade:
        trade['momentum_last_candle_time'] = current_time
        trade['momentum_candle_count'] = 0
        if logger.should_log('MOMENTUM'):
            logger.log(f"[MOMENTUM] {symbol}: Iniciando conteo de {momentum_candles} velas de {tf} para objetivo {momentum_threshold}%", "MOMENTUM", "info")
    
    time_since_last_candle = current_time - trade['momentum_last_candle_time']
    if time_since_last_candle >= seconds_per_candle:
        trade['momentum_candle_count'] = trade.get('momentum_candle_count', 0) + 1
        trade['momentum_last_candle_time'] = current_time
        
        if logger.should_log('MOMENTUM'):
            logger.log(f"[MOMENTUM] {symbol}: Vela #{trade['momentum_candle_count']} completada ({tf}). ROI máximo actual: {trade.get('momentum_max_roi', 0):.2f}%", "MOMENTUM", "debug")
    
    if current_roi > trade.get('momentum_max_roi', 0):
        trade['momentum_max_roi'] = current_roi
    
    min_target_reached = trade.get('momentum_max_roi', 0) >= momentum_threshold
    if int(current_time) % 30 == 0 and logger.should_log('MOMENTUM'):
        logger.log(f"[MOMENTUM] {symbol}: Vela {trade.get('momentum_candle_count', 0)}/{momentum_candles}, ROI máx: {trade.get('momentum_max_roi', 0):.2f}%", "MOMENTUM", "debug")
    if trade.get('momentum_candle_count', 0) >= momentum_candles and not min_target_reached:
        try:
            kl = client.futures_klines(symbol=symbol, interval=tf, limit=50)
            if kl and len(kl) >= 2:
                closes = [float(k[4]) for k in kl]
                current_close = closes[-1]
                
                ema_fast = calcular_ema(closes, int(DEFAULT_CONFIG['ema_fast_entry']))
                
                if ema_fast:
                    direction = trade['direction']
                    lost_ema = False
                    
                    if direction == "LONG" and current_close < ema_fast:
                        lost_ema = True
                    elif direction == "SHORT" and current_close > ema_fast:
                        lost_ema = True
                    
                    if lost_ema:
                        if logger.should_log('MOMENTUM'):
                            logger.log(f"{symbol}: ⚡ MOMENTUM LOSS detectado! ROI máximo: {trade['momentum_max_roi']:.2f}% (esperado: {momentum_threshold}%)", "MOMENTUM", "momentum")
                            logger.log(f"{symbol}: Perdió EMA rápida. Cerrando posición...", "MOMENTUM", "momentum")
                        
                        try:
                            client.futures_cancel_all_open_orders(symbol=symbol)
                            time.sleep(0.5)
                        except:
                            pass
                        
                        position_qty = trade['qty']
                        side_close = SIDE_SELL if direction == "LONG" else SIDE_BUY
                        
                        client.futures_create_order(
                            symbol=symbol,
                            side=side_close,
                            type="MARKET",
                            quantity=position_qty
                        )
                        
                        entry_price = trade['entry_price']
                        exit_price = current_price
                        
                        if direction == "LONG":
                            pnl_usdt = (exit_price - entry_price) * position_qty
                        else:
                            pnl_usdt = (entry_price - exit_price) * position_qty
                        
                        capital = (position_qty * entry_price) / trade.get('leverage', 1)
                        roi_percent = (pnl_usdt / capital) * 100 if capital > 0 else 0
                        
                        duracion_segundos = int(time.time() - trade.get('open_time', time.time()))
                        
                        use_ema = use_ema_var.get()
                        use_cci = use_cci_var.get()
                        estrategia = "EMA" if use_ema and not use_cci else \
                                   "CCI" if use_cci and not use_ema else \
                                   "EMA+CCI" if use_ema and use_cci else "DESCONOCIDA"
                        
                        registrar_trade_para_reporte(
                            symbol=symbol,
                            trade_type=direction,
                            entry_price=entry_price,
                            exit_price=exit_price,
                            roi_percent=roi_percent,
                            pnl_usdt=pnl_usdt,
                            estrategia=estrategia,
                            motivo="MOMENTUM_LOSS",
                            duracion_segundos=duracion_segundos
                        )
                        
                        signo = "+" if pnl_usdt > 0 else ""
                        resultado = "GANANCIA" if pnl_usdt > 0 else "PERDIDA"
                        color = "profit" if pnl_usdt > 0 else "error"
                        
                        if logger.should_log('MOMENTUM'):
                            logger.log_separator(f"⚡ MOMENTUM LOSS - {symbol} CERRADO", "MOMENTUM")
                            logger.log(f"Par: {symbol}", "MOMENTUM")
                            logger.log(f"Dirección: {direction}", "MOMENTUM")
                            logger.log(f"Entrada: {entry_price:.8f}", "MOMENTUM")
                            logger.log(f"Salida: {exit_price:.8f}", "MOMENTUM")
                            logger.log(f"ROI: {signo}{roi_percent:.2f}%", "MOMENTUM", color)
                            logger.log(f"P&L: {signo}{pnl_usdt:.6f} USDT", "MOMENTUM", color)
                            logger.log(f"Motivo: MOMENTUM_LOSS (no alcanzó {momentum_threshold}% en {momentum_candles} velas)", "MOMENTUM")
                            logger.log(f"ROI máximo alcanzado: {trade['momentum_max_roi']:.2f}%", "MOMENTUM")
                            logger.log(f"Duración: {duracion_segundos}s", "MOMENTUM")
                            logger.log_separator("", "MOMENTUM")
                        
                        trade['momentum_loss_evaluated'] = True
                        return True
        
        except Exception as e:
            # ESTA LÍNEA DEBE SER "ERROR" NO "MOMENTUM" - PERO DEBE RESPETAR FILTRO DE ERROR
            logger.log(f"Error en Momentum Loss check para {symbol}: {e}", "ERROR", "error")
    
    if min_target_reached:
        trade['momentum_loss_evaluated'] = True
        if logger.should_log('MOMENTUM'):
            logger.log(f"{symbol}: ✅ Objetivo Momentum alcanzado ({trade['momentum_max_roi']:.2f}% ≥ {momentum_threshold}%)", "MOMENTUM", "success")
    
    return False

# ============================================================
# MONITOREO DE POSICIONES CON TRAILING JERÁRQUICO
# ============================================================
def monitoring_loop():
    while bot_running:
        try:
            global symbols_with_positions
            current_positions_on_exchange = get_symbols_with_positions()
            
            previously_active = symbols_with_positions.copy()
            newly_closed = previously_active - current_positions_on_exchange
            
            for symbol in newly_closed:
                if symbol in active_trades:
                    trade = active_trades[symbol]
                    try:
                        positions = client.futures_position_information(symbol=symbol)
                        if positions:
                            position_info = positions[0]
                            if float(position_info['positionAmt']) != 0:
                                logger.log(
                                    f"{symbol}: Advertencia: cierre local pero posición sigue abierta en Binance.",
                                    "ERROR", "error"
                                )
                                continue
                            
                            entry_price = trade['entry_price']
                            exit_price = float(position_info.get('markPrice', 0))
                            direction = trade['direction']
                            position_qty = trade.get('qty_restante', trade.get('qty', 0))
                            leverage = trade.get('leverage', float(leverage_entry.get()))
                            capital = (position_qty * entry_price) / leverage
                            
                            if direction == "LONG":
                                pnl_usdt = (exit_price - entry_price) * position_qty
                            else:
                                pnl_usdt = (entry_price - exit_price) * position_qty
                            
                            roi_percent = (pnl_usdt / capital) * 100 if capital > 0 else 0
                            motivo = "TP" if pnl_usdt > 0 else "SL" if pnl_usdt < 0 else "OTRO"
                            
                            # NUEVO: Registrar nivel alcanzado
                            nivel_alcanzado = trade.get('current_level', 0)
                            if nivel_alcanzado > 0:
                                motivo += f" (Nivel {nivel_alcanzado})"
                            
                            registrar_trade_para_reporte(
                                symbol, direction, entry_price, exit_price,
                                roi_percent, pnl_usdt, "AUTO", motivo, 0
                            )
                    except Exception as e:
                        logger.log(f"Error al procesar trade cerrado {symbol}: {e}", "ERROR", "error")
                    
                    del active_trades[symbol]
            
            symbols_with_positions = current_positions_on_exchange
            
            if symbols_with_positions:
                positions_info = client.futures_position_information()
                
                leverage = float(leverage_entry.get())
                break_enabled = break_var.get()
                trailing_enabled = trailing_var.get()
                break_percent = float(break_percent_entry.get())
                trailing_activate_percent = float(trailing_activate_entry.get())
                trailing_distance_percent = float(trailing_distance_entry.get())
                
                for info in positions_info:
                    symbol = info['symbol']
                    position_amt = float(info['positionAmt'])
                    
                    if abs(position_amt) > 0:
                        trade = active_trades.get(symbol)
                        
                        if trade is None:
                            logger.log(
                                f"{symbol}: Posición activa detectada pero sin registro local. Intentando adoptarla...",
                                "INFO", "warning"
                            )
                            
                            time.sleep(2.5)
                            open_orders = client.futures_get_open_orders(symbol=symbol)
                            
                            existing_sl = any(
                                o['type'] == "STOP_MARKET" and o.get('closePosition') == True
                                for o in open_orders
                            )
                            existing_tp = any(
                                o['type'] == "TAKE_PROFIT_MARKET" and o.get('closePosition') == True
                                for o in open_orders
                            )
                            
                            trade = {
                                'symbol': symbol,
                                'entry_price': float(info['entryPrice']),
                                'direction': "LONG" if position_amt > 0 else "SHORT",
                                'qty': abs(position_amt),
                                'qty_restante': abs(position_amt),
                                'break_even_reached': existing_sl,
                                'trailing_activated': False,
                                'sl_id': None,
                                'leverage': get_leverage(symbol),
                                'open_time': time.time(),
                                'current_level': 0,  # NUEVO
                                'levels_activated': [],  # NUEVO
                                'momentum_last_candle_time': time.time() if momentum_loss_var.get() else 0,
                                'momentum_candle_count': 0,
                                'momentum_loss_evaluated': not momentum_loss_var.get(),
                            }
                            active_trades[symbol] = trade
                            
                            if existing_sl and existing_tp:
                                logger.log(
                                    f"{symbol}: ✅ Posición adoptada con SL/TP existente. No se toca.",
                                    "ORDERS", "success"
                                )
                                continue
                            
                            logger.log(
                                f"{symbol}: 🔴 ALERTA: Posición SIN SL/TP detectada. Colocando protección...",
                                "ERROR", "error"
                            )
                            
                            success = colocar_ordenes_simple(
                                symbol,
                                trade['direction'],
                                trade['entry_price'],
                                trade['qty']
                            )
                            
                            if not success:
                                final_orders = client.futures_get_open_orders(symbol=symbol)
                                existe_proteccion = any(
                                    o['type'] in ("STOP_MARKET", "TAKE_PROFIT_MARKET")
                                    and o.get('closePosition') == True
                                    for o in final_orders
                                )
                                
                                if existe_proteccion:
                                    logger.log(
                                        f"{symbol}: ⚠️ Binance ya tenía SL/TP. Se adopta posición y NO se cierra.",
                                        "ORDERS", "warning"
                                    )
                                    trade['break_even_reached'] = True
                                    continue
                                
                                logger.log(
                                    f"{symbol}: ❌ FALLO REAL: sin protección. Cerrando por seguridad.",
                                    "ERROR", "error"
                                )
                                side_close = SIDE_SELL if trade['direction'] == "LONG" else SIDE_BUY
                                client.futures_create_order(
                                    symbol=symbol,
                                    side=side_close,
                                    type="MARKET",
                                    quantity=trade['qty']
                                )
                                del active_trades[symbol]
                                continue
                        
                        # Calcular ROI actual
                        entry_price = trade['entry_price']
                        current_price = float(info.get('markPrice', entry_price))
                        position_qty = trade.get('qty_restante', trade.get('qty', 0))
                        
                        if entry_price > 0 and current_price > 0 and position_qty > 0:
                            if trade['direction'] == "LONG":
                                pnl = (current_price - entry_price) * position_qty
                            else:
                                pnl = (entry_price - current_price) * position_qty
                            
                            capital = (position_qty * entry_price) / trade.get('leverage', leverage)
                            current_roi = (pnl / capital) * 100 if capital > 0 else 0
                            
                            # NUEVO: Verificar trailing jerárquico primero
                            hierarchical_applied = False
                            if trailing_enabled and current_roi >= trailing_activate_percent:
                                hierarchical_applied = apply_hierarchical_trailing(symbol, trade, current_roi, current_price)
                            
                            # Si no se aplicó trailing jerárquico (o está desactivado), usar trailing simple
                            if not hierarchical_applied and trailing_enabled and current_roi >= trailing_activate_percent:
                                if not trade.get('trailing_activated', False):
                                    # Trailing simple (solo si no hay jerárquico)
                                    trailing_distance = trailing_distance_percent
                                    if trade['direction'] == "LONG":
                                        new_sl_price = current_price * (1 - (trailing_distance / leverage) / 100)
                                    else:
                                        new_sl_price = current_price * (1 + (trailing_distance / leverage) / 100)
                                    
                                    try:
                                        tick_size = get_tick_size(symbol)
                                        formatted_sl_price = round_to_tick(new_sl_price, tick_size)
                                        formatted_sl_price = f"{formatted_sl_price:.8f}".rstrip('0').rstrip('.')
                                        
                                        if trade.get('sl_id'):
                                            try:
                                                client.futures_cancel_order(symbol=symbol, orderId=trade['sl_id'])
                                                time.sleep(0.2)
                                            except:
                                                pass
                                        
                                        side_order = SIDE_SELL if trade['direction'] == "LONG" else SIDE_BUY
                                        order = client.futures_create_order(
                                            symbol=symbol,
                                            side=side_order,
                                            type="STOP_MARKET",
                                            closePosition=True,
                                            stopPrice=formatted_sl_price,
                                            timeInForce=TIME_IN_FORCE_GTC
                                        )
                                        
                                        trade['sl_id'] = order.get('orderId')
                                        trade['trailing_activated'] = True
                                        
                                        logger.log(
                                            f"{symbol}: 🚀 TRAILING SIMPLE ACTIVADO @ {formatted_sl_price} (ROI: {current_roi:.2f}%)",
                                            "ORDERS", "trailing"
                                        )
                                    except Exception as e:
                                        logger.log(f"Error activando trailing simple en {symbol}: {e}", "ERROR", "error")
                            
                            # Break-even logic
                            if break_enabled and not trade.get('break_even_reached', False) and current_roi >= break_percent:
                                try:
                                    tick_size = get_tick_size(symbol)
                                    
                                    if trade['direction'] == "LONG":
                                        be_price = entry_price
                                    else:
                                        be_price = entry_price
                                    
                                    formatted_be_price = round_to_tick(be_price, tick_size)
                                    formatted_be_price = f"{formatted_be_price:.8f}".rstrip('0').rstrip('.')
                                    
                                    if trade.get('sl_id'):
                                        try:
                                            client.futures_cancel_order(symbol=symbol, orderId=trade['sl_id'])
                                            time.sleep(0.2)
                                        except:
                                            pass
                                    
                                    side_order = SIDE_SELL if trade['direction'] == "LONG" else SIDE_BUY
                                    order = client.futures_create_order(
                                        symbol=symbol,
                                        side=side_order,
                                        type="STOP_MARKET",
                                        closePosition=True,
                                        stopPrice=formatted_be_price,
                                        timeInForce=TIME_IN_FORCE_GTC
                                    )
                                    
                                    trade['sl_id'] = order.get('orderId')
                                    trade['break_even_reached'] = True
                                    
                                    logger.log(
                                        f"{symbol}: 🛡️ BREAK-EVEN ACTIVADO @ {formatted_be_price}",
                                        "ORDERS", "break_even"
                                    )
                                except Exception as e:
                                    logger.log(f"Error activando break-even en {symbol}: {e}", "ERROR", "error")
                            
                            # Momentum Loss check
                            check_momentum_loss(symbol, trade, current_price, current_roi)
            
            time.sleep(1)
        except Exception as e:
            if bot_running:
                logger.log(f"Error CRÍTICO en monitoring_loop: {e}", "ERROR", "error")
            time.sleep(5)

# ============================================================
# CICLO PRINCIPAL DEL BOT CON FOCUS MODE - MEJORADO
# ============================================================
def get_shitcoin_list():
    global all_shitcoins, last_coin_refresh
    current_time = time.time()
    
    if current_time - last_coin_refresh < COIN_REFRESH_INTERVAL and all_shitcoins:
        return all_shitcoins
    
    try:
        logger.log("Refrescando lista de Shitcoins...", "INFO", "rotator")
        exchange_info = client.futures_exchange_info()
        
        min_price = float(min_price_entry.get())
        max_price = float(max_price_entry.get())
        min_volume = float(min_volume_entry.get())
        
        futures_symbols = [s for s in exchange_info['symbols'] 
                          if s['symbol'].endswith('USDT') 
                          and s['status'] == 'TRADING']
        
        prices = client.futures_ticker()
        price_map = {p['symbol']: float(p['lastPrice']) for p in prices}
        
        filtered_by_price = [s for s in futures_symbols 
                            if min_price <= price_map.get(s['symbol'], 0) <= max_price]
        
        ticker_24h = client.futures_ticker()
        
        shitcoins_list = []
        for ticker in ticker_24h:
            symbol = ticker['symbol']
            if symbol.endswith('USDT'):
                volume = float(ticker.get('quoteVolume', 0))
                price = price_map.get(symbol, 0)
                
                if min_price <= price <= max_price and volume >= min_volume:
                    shitcoins_list.append({
                        'symbol': symbol,
                        'volume': volume,
                        'price': price
                    })
        
        shitcoins_list.sort(key=lambda x: x['volume'], reverse=True)
        
        all_shitcoins = shitcoins_list
        last_coin_refresh = current_time
        logger.log(f"Lista de Shitcoins actualizada. {len(all_shitcoins)} monedas cumplen el criterio.", "INFO", "rotator")
        return all_shitcoins
    
    except Exception as e:
        logger.log(f"Error al obtener lista de shitcoins: {e}", "ERROR", "error")
        return []

def get_next_cycle_coins():
    try:
        lista_completa = get_shitcoin_list()
        if not lista_completa:
            return []
        
        user_limit = int(shitcoins_per_cycle_entry.get().strip())
        monedas_por_ciclo = min(user_limit, 15)
        
        if not hasattr(get_next_cycle_coins, 'indice_rotacion'):
            get_next_cycle_coins.indice_rotacion = 0
        
        total_monedas = len(lista_completa)
        inicio = get_next_cycle_coins.indice_rotacion
        fin = inicio + monedas_por_ciclo
        
        if fin > total_monedas:
            inicio = 0
            fin = monedas_por_ciclo
            get_next_cycle_coins.indice_rotacion = 0
        
        seleccionadas = lista_completa[inicio:fin]
        get_next_cycle_coins.indice_rotacion = fin
        
        simbolos_seleccionados = [coin['symbol'] for coin in seleccionadas]
        
        return simbolos_seleccionados
        
    except Exception as e:
        logger.log(f"Error en selección de ciclo: {e}", "ERROR", "error")
        lista_completa = get_shitcoin_list()
        lista_completa.sort(key=lambda x: x['volume'], reverse=True)
        return [coin['symbol'] for coin in lista_completa[:10]]

def bot_cycle_thread():
    if not hasattr(bot_cycle_thread, 'ciclo_count'):
        bot_cycle_thread.ciclo_count = 0
    
    while bot_running:
        try:
            # ===== CHECK FOCUS MODE =====
            focus_mode_active = False
            try:
                max_trades = int(max_trades_entry.get().strip())
                active_count = len(symbols_with_positions)
                
                # Focus Mode: Si alcanzamos el máximo, solo monitoreamos
                if active_count >= max_trades and DEFAULT_CONFIG.get('focus_mode_enabled', 1):
                    if not hasattr(bot_cycle_thread, 'focus_mode_entered'):
                        bot_cycle_thread.focus_mode_entered = True
                        logger.log(f"🔴 FOCUS MODE ACTIVADO: {active_count}/{max_trades} trades. "
                                 f"Escaneo PAUSADO. Solo monitoreo activo.", "INFO", "focus")
                    
                    focus_mode_active = True
                    
                    # Solo monitorear, no escanear nuevas monedas
                    time.sleep(5)
                    continue
                else:
                    if hasattr(bot_cycle_thread, 'focus_mode_entered'):
                        if bot_cycle_thread.focus_mode_entered:
                            logger.log(f"🟢 FOCUS MODE DESACTIVADO: {active_count}/{max_trades} trades. "
                                     f"Escaneo REANUDADO.", "INFO", "focus")
                        bot_cycle_thread.focus_mode_entered = False
            except ValueError:
                pass
            # ===== FIN FOCUS MODE =====
            
            coins_to_check = get_next_cycle_coins()
            
            bot_cycle_thread.ciclo_count += 1
            status_vars['ciclo'].set(f"#{bot_cycle_thread.ciclo_count}")
            
            if bot_cycle_thread.ciclo_count % 10 == 0:
                if focus_mode_active:
                    logger.log(f"Ciclo #{bot_cycle_thread.ciclo_count} - FOCUS MODE ACTIVO (solo monitoreo)", 
                              "INFO", "focus")
                else:
                    logger.log(f"Ciclo #{bot_cycle_thread.ciclo_count} - Analizando {len(coins_to_check)} monedas", 
                              "INFO", "timeframe")
            
            # ===== ESCANEO ASYNC PARALELO =====
            if coins_to_check and not focus_mode_active:
                logger.log(f"Escaneando {len(coins_to_check)} monedas en paralelo (async)...", "INFO", "timeframe")
                results = run_async_scan(coins_to_check)
                
                signals_detected = 0
                for result in results:
                    if not bot_running:
                        return
                    
                    # VERIFICAR que result no sea None y tenga 3 elementos
                    if not result:
                        continue
                    if len(result) != 3:
                        continue
                    
                    symbol, signal, cci_signal = result
                    
                    if signal and symbol not in symbols_with_positions:
                        # Verificar límite de trades nuevamente (pudo cambiar durante el escaneo)
                        try:
                            max_trades = int(max_trades_entry.get().strip())
                            if len(symbols_with_positions) >= max_trades:
                                continue
                        except:
                            continue
                        
                        signals_detected += 1
                        if open_trade_simple(symbol, signal, cci_signal):
                            logger.log(f"Trade exitoso en {symbol} (escaneo async)", "TRADE", "success")
                
                if signals_detected > 0:
                    logger.log(f"Se detectaron {signals_detected} señales en este ciclo", "TRADE", "trade")
            # ===== FIN DE NUEVO CÓDIGO =====
            
            try:
                timeframe_seconds = int(timeframe_var.get().replace('m', '')) * 60
            except:
                timeframe_seconds = 180 
            
            sleep_time = max(10, timeframe_seconds / 5)
            time.sleep(sleep_time)
        
        except Exception as e:
            if bot_running:
                logger.log(f"Error en bot_cycle_thread: {e}", "ERROR", "error")
                register_error(str(e))
            time.sleep(10)

# ============================================================
# FUNCIONES DE CONTROL DE THREADS - MEJORADO
# ============================================================
def start_bot_thread():
    global bot_running, symbols_with_positions
    if bot_lock.acquire(blocking=False):
        try:
            # Asegurar que los logs INFO se muestren al iniciar
            if logger:
                logger.set_filter('INFO', True)
            
            # --- PASO CRÍTICO: Cargar configuración ANTES de usar los valores ---
            cargar_configuracion()
            
            if not conectar_binance():
                bot_lock.release()
                return
            
            symbols_with_positions = get_symbols_with_positions()
            
            bot_running = True
            
            actualizar_panel.start_time = time.time()
            
            if hasattr(detect_breakout_simple, 'signals_count'):
                detect_breakout_simple.signals_count = 0
            if hasattr(bot_cycle_thread, 'ciclo_count'):
                bot_cycle_thread.ciclo_count = 0
            
            logger.log_separator("INICIANDO BOT v4.1 - TRAILING JERÁRQUICO", "INFO")
            modo = "💰 MODO REAL" if paper_var.get() == 0 else "🧪 MODO PAPER TRADING"
            logger.log(f"{modo}", "INFO", "trade")
            logger.log(f"TP: {tp_entry.get()}% | SL: {sl_entry.get()}%", "INFO")
            logger.log(f"Capital: {capital_entry.get()} USDT | Leverage: {leverage_entry.get()}x", "INFO")
            logger.log(f"Timeframe: {timeframe_var.get()} | Máx Trades: {max_trades_entry.get()}", "INFO")
            
            # --- TRAILING STOP (CON VALORES) ---
            if trailing_var.get():
                act_val = trailing_activate_entry.get()
                dist_val = trailing_distance_entry.get()
                logger.log(f"TRAILING STOP: Activado a {act_val}% | Distancia: {dist_val}%", "INFO", "trailing")
            else:
                logger.log(f"TRAILING STOP: Desactivado", "INFO", "info")
            
            # --- TRAILING JERÁRQUICO (NUEVO) - CON DETALLES COMPLETOS ---
            hierarchical_config = DEFAULT_CONFIG['trailing_hierarchical']
            hierarchical_enabled = hierarchical_config.get('enabled', 0)
            
            if hierarchical_enabled:
                logger.log(f"🎯 TRAILING JERÁRQUICO: ACTIVADO", "INFO", "trailing")
                levels = hierarchical_config.get('levels', [])
                for i, level in enumerate(levels, 1):
                    if level['move_sl_to'] == 'dynamic':
                        logger.log(f"  Nivel {i}: +{level['activate_at']}% → Trailing ±{level.get('trailing_distance', 2.0)}%", "INFO", "trailing")
                    else:
                        logger.log(f"  Nivel {i}: +{level['activate_at']}% → SL a +{level['move_sl_to']}%", "INFO", "trailing")
            else:
                logger.log(f"🎯 TRAILING JERÁRQUICO: DESACTIVADO (usar clásico)", "INFO", "info")
            
            # --- FOCUS MODE (NUEVO) ---
            focus_enabled = DEFAULT_CONFIG.get('focus_mode_enabled', 1)
            if focus_enabled:
                logger.log(f"🎯 FOCUS MODE: ACTIVADO (pausa escaneo al máximo trades)", "INFO", "focus")
            else:
                logger.log(f"🎯 FOCUS MODE: DESACTIVADO", "INFO", "info")
            
            # --- BREAK-EVEN (CON VALOR) ---
            if break_var.get():
                be_val = break_percent_entry.get()
                logger.log(f"BREAK-EVEN: Activado a {be_val}%", "INFO", "break_even")
            else:
                logger.log(f"BREAK-EVEN: Desactivado", "INFO", "info")
            
            # --- MOMENTUM & ANTI-SWEEP (CON SENSIBILIDAD) ---
            momentum_active = "ACTIVADO" if momentum_loss_var.get() else "DESACTIVADO"
            anti_sweep_active = "ACTIVADO" if anti_sweep_var.get() else "DESACTIVADO"
            logger.log(f"Momentum Loss: {momentum_active}", "INFO", "momentum")
            logger.log(f"Anti-Sweep: {anti_sweep_active} (Sens: {anti_sweep_sensibilidad_var.get()}%)", "INFO", "strategy")
            
            if use_ema_var.get() or use_cci_var.get():
                estrategia = []
                if use_ema_var.get():
                    estrategia.append(f"EMA({DEFAULT_CONFIG['ema_fast_entry']}/{DEFAULT_CONFIG['ema_slow_entry']})")
                if use_cci_var.get():
                    estrategia.append(f"CCI({DEFAULT_CONFIG['cci_period_entry']})")
                logger.log(f"Estrategia: {' | '.join(estrategia)}", "INFO", "strategy")
            
            logger.log(f"🚀 Escaneo Async: ACTIVADO (hasta 15 monedas en paralelo)", "INFO", "success")
            logger.log_separator("", "INFO")
            
            threading.Thread(target=monitoring_loop, daemon=True).start()
            threading.Thread(target=bot_cycle_thread, daemon=True).start()
        
        except Exception as e:
            logger.log(f"Error al iniciar el bot: {e}", "ERROR", "error")
            register_error(str(e))
            stop_bot(release_lock=False)
        finally:
            if bot_lock.locked():
                bot_lock.release()

def stop_bot(release_lock=True):
    global bot_running, async_client_instance
    
    # Simplificar: si el bot no está corriendo, solo log y salir
    if not bot_running:
        logger.log("El bot ya está detenido.", "INFO", "warning")
        return
    
    # Marcar como detenido inmediatamente
    bot_running = False
    
    # Cerrar el cliente async si existe
    if async_client_instance:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_client_instance.close_connection())
            loop.close()
        except:
            pass
        async_client_instance = None
    
    logger.log("BOT DETENIDO. Cerrando hilos y limpiando async...", "INFO", "error")
    set_led_status('off')
    
    # Liberar el lock si está adquirido
    try:
        if bot_lock.locked():
            bot_lock.release()
    except:
        pass
    
    time.sleep(0.5)

# ============================================================
# INICIALIZACIÓN - MEJORADO CON DETALLES DE NIVELES
# ============================================================
if __name__ == '__main__':
    if sys.platform.startswith('win'):
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    cargar_configuracion()
    
    logger.log_separator("SHITCOIN WHISPERER PROFESSIONAL v4.1 - TRAILING JERÁRQUICO", "INFO")
    logger.log(f"Versión: {VERSION}", "INFO")
    logger.log(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    logger.log("Filtros: ERROR, TRADE, ORDERS, MOMENTUM activados | INFO desactivado", "INFO")
    logger.log("Panel de estado en vivo ACTIVADO", "INFO")
    logger.log("🚀 Escaneo Async: ACTIVADO (Semaforo: 15, Timeout: 20s)", "INFO", "success")
    logger.log_separator("", "INFO")
    
    # NUEVO: Mostrar configuración de trailing jerárquico CON DETALLES
    hierarchical_config = DEFAULT_CONFIG['trailing_hierarchical']
    if hierarchical_config.get('enabled', 0):
        logger.log("🎯 TRAILING JERÁRQUICO CONFIGURADO:", "INFO", "trailing")
        levels = hierarchical_config.get('levels', [])
        for i, level in enumerate(levels, 1):
            if level['move_sl_to'] == 'dynamic':
                logger.log(f"  Nivel {i}: +{level['activate_at']}% → Trailing Dinámico (±{level.get('trailing_distance', 2.0)}%)", "INFO", "trailing")
            else:
                logger.log(f"  Nivel {i}: +{level['activate_at']}% → SL a +{level['move_sl_to']}%", "INFO", "trailing")
    else:
        logger.log("🎯 TRAILING JERÁRQUICO: DESACTIVADO (usar trailing clásico)", "INFO", "info")
    
    # NUEVO: Mostrar Focus Mode status
    focus_enabled = DEFAULT_CONFIG.get('focus_mode_enabled', 1)
    if focus_enabled:
        logger.log("🎯 FOCUS MODE: ACTIVADO (pausa escaneo al alcanzar máximo trades)", "INFO", "focus")
    else:
        logger.log("🎯 FOCUS MODE: DESACTIVADO", "INFO", "info")
    
    use_ema = use_ema_var.get()
    use_cci = use_cci_var.get()
    
    if use_ema or use_cci:
        logger.log("ESTRATEGIA CONFIGURADA:", "INFO", "strategy")
        if use_ema:
            logger.log(f"  • EMA: Rápida({DEFAULT_CONFIG['ema_fast_entry']}) / Lenta({DEFAULT_CONFIG['ema_slow_entry']})", "INFO", "strategy")
        if use_cci:
            logger.log(f"  • CCI: Período({DEFAULT_CONFIG['cci_period_entry']}) | Límites[{DEFAULT_CONFIG['cci_lower_entry']}, {DEFAULT_CONFIG['cci_upper_entry']}]", "INFO", "strategy")
    else:
        logger.log("ADVERTENCIA: No hay estrategia activa. Active EMA y/o CCI.", "INFO", "warning")
    
    if momentum_loss_var.get():
        threshold = DEFAULT_CONFIG['momentum_loss_threshold_entry']
        candles = DEFAULT_CONFIG['momentum_loss_candles_entry']
        logger.log(f"⚡ Momentum Loss: ACTIVADO | Objetivo: {threshold}% en {candles} velas", "INFO", "momentum")
    else:
        logger.log("⚡ Momentum Loss: DESACTIVADO", "INFO", "warning")
    
    if anti_sweep_var.get():
        logger.log("🛡️ Anti-Sweep MM: ACTIVADO (Protección contra trampas)", "INFO", "strategy")
    else:
        logger.log("🛡️ Anti-Sweep MM: DESACTIVADO", "INFO", "warning")
    
    logger.log("💾 Configuraciones mejoradas: Trailing Jerárquico + Focus Mode", "INFO", "success")
    
    root.mainloop()