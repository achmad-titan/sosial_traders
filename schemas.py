from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str
    
class TambahAkunTrading(BaseModel):
    nomor_akun: str
    nama_server: str
    saldo: float
    profit_persen: float = 0.0
    
class BuatPostingan(BaseModel):
    isi_teks: str
    
class BuatLaporan(BaseModel):
    alasan: str