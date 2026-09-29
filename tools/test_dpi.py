import ctypes


user32 = ctypes.windll.user32
shcore = ctypes.windll.shcore


print("=== BEFORE ===")
print("Process DPI aware:", user32.IsProcessDPIAware())
print("System DPI:", user32.GetDpiForSystem())
print("Scale factor:", shcore.GetScaleFactorForDevice(0))


print()
print("=== SET PROCESS DPI AWARE ===")

result = user32.SetProcessDPIAware()

print("SetProcessDPIAware:", result)


print()
print("=== AFTER ===")
print("Process DPI aware:", user32.IsProcessDPIAware())
print("System DPI:", user32.GetDpiForSystem())
print("Scale factor:", shcore.GetScaleFactorForDevice(0))
