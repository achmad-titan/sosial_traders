from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

import models, schemas
from database import engine, get_db

# Membuat tabel otomatis
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Social Traders API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "kunci_rahasia_sosial_traders_32x!"  # minimal 32 karakter agar tidak ada warning JWT
ALGORITHM = "HS256"


# ─────────────────────────────────────────────
#  STATIC FILES — semua HTML/CSS/JS dilayani
#  dari folder yang sama dengan main.py
#  Akses: http://localhost:8000/index.html
# ─────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", response_class=FileResponse)
def root():
    return FileResponse("index.html")

# Tangkap semua route .html agar bisa diakses langsung
# misal: http://localhost:8000/dashboard.html
@app.get("/{page}.html", response_class=FileResponse)
def serve_page(page: str):
    import os
    path = f"{page}.html"
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Halaman tidak ditemukan")


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
@app.post("/signup")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    cek_email = db.query(models.User).filter(models.User.email == user.email).first()
    if cek_email:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar!")
    cek_username = db.query(models.User).filter(models.User.username == user.username).first()
    if cek_username:
        raise HTTPException(status_code=400, detail="Username sudah dipakai!")
    hashed_password = pwd_context.hash(user.password)
    user_baru = models.User(email=user.email, username=user.username, password=hashed_password)
    db.add(user_baru)
    db.commit()
    db.refresh(user_baru)
    return {"pesan": "User berhasil dibuat!", "username": user_baru.username}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Email tidak ditemukan!")
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Password salah!")
    batas_waktu = datetime.utcnow() + timedelta(hours=24)  # diperpanjang jadi 24 jam
    data_token = {"sub": db_user.email, "exp": batas_waktu}
    token = jwt.encode(data_token, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "pesan": "Login berhasil!",
        "access_token": token,
        "token_type": "bearer"
    }


def ambil_user_saat_ini(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token tidak valid!")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token sudah kedaluwarsa, silakan login ulang!")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid!")
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User tidak ditemukan!")
    return user


# ─────────────────────────────────────────────
#  PROFIL
# ─────────────────────────────────────────────
@app.get("/profil")
def lihat_profil(user_sekarang: models.User = Depends(ambil_user_saat_ini)):
    return {
        "pesan": "Selamat datang!",
        "data_user": {
            "id": user_sekarang.id,
            "email": user_sekarang.email,
            "username": user_sekarang.username,
            "profil_publik": user_sekarang.is_public
        }
    }


@app.get("/profil-publik/{username_tujuan}")
def cari_profil(username_tujuan: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username_tujuan,
        models.User.is_public == True
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profil tidak ditemukan atau disetel Private!")
    data_akun = [
        {
            "server": a.nama_server,
            "saldo": a.saldo,
            "profit_persen": a.profit_persen if hasattr(a, 'profit_persen') else 0
        }
        for a in user.akun_trading
    ]
    return {
        "username": user.username,
        "status": "Publik",
        "portofolio_trading": data_akun
    }


# ─────────────────────────────────────────────
#  DASHBOARD & AKUN TRADING
# ─────────────────────────────────────────────
@app.get("/user/dashboard")
def dashboard_saya(user_sekarang: models.User = Depends(ambil_user_saat_ini)):
    daftar_akun = [
        {
            "nomor_akun": akun.nomor_akun,
            "server": akun.nama_server,
            "saldo": akun.saldo,
            "profit_persen": akun.profit_persen if hasattr(akun, 'profit_persen') else 0
        }
        for akun in user_sekarang.akun_trading
    ]
    return {
        "user": user_sekarang.username,
        "email": user_sekarang.email,
        "total_akun": len(daftar_akun),
        "daftar_akun": daftar_akun
    }


@app.post("/tambah-akun-trading")
def tambah_akun(
    data_akun: schemas.TambahAkunTrading,
    db: Session = Depends(get_db),
    user_sekarang: models.User = Depends(ambil_user_saat_ini)
):
    cek_akun = db.query(models.TradingAccount).filter(
        models.TradingAccount.nomor_akun == data_akun.nomor_akun
    ).first()
    if cek_akun:
        raise HTTPException(status_code=400, detail="Nomor akun ini sudah terdaftar!")
    akun_baru = models.TradingAccount(
        nomor_akun=data_akun.nomor_akun,
        nama_server=data_akun.nama_server,
        saldo=data_akun.saldo,
        profit_persen=data_akun.profit_persen if hasattr(data_akun, 'profit_persen') else 0,
        user_id=user_sekarang.id
    )
    db.add(akun_baru)
    db.commit()
    db.refresh(akun_baru)
    return {"pesan": "Akun trading berhasil ditambahkan!", "data": akun_baru}


# ─────────────────────────────────────────────
#  PRIVASI
# ─────────────────────────────────────────────
@app.put("/user/update-privasi")
def update_privasi(
    status_baru: bool,
    db: Session = Depends(get_db),
    user_sekarang: models.User = Depends(ambil_user_saat_ini)
):
    user_sekarang.is_public = status_baru
    db.commit()
    return {"pesan": f"Status profil berhasil diubah menjadi {'Publik' if status_baru else 'Private'}"}


# ─────────────────────────────────────────────
#  LEADERBOARD
# ─────────────────────────────────────────────
@app.get("/leaderboard")
def lihat_leaderboard(db: Session = Depends(get_db)):
    users_publik = db.query(models.User).filter(models.User.is_public == True).all()
    hasil = []
    for user in users_publik:
        akun = user.akun_trading
        if akun:
            hasil.append({
                "username": user.username,
                "jumlah_akun": len(akun),
                "total_saldo": sum(a.saldo for a in akun)
            })
    return {"leaderboard": sorted(hasil, key=lambda x: x["total_saldo"], reverse=True)}


# ─────────────────────────────────────────────
#  FOLLOW
# ─────────────────────────────────────────────
@app.post("/follow/{username_tujuan}")
def follow_user(
    username_tujuan: str,
    db: Session = Depends(get_db),
    user_sekarang: models.User = Depends(ambil_user_saat_ini)
):
    target_user = db.query(models.User).filter(models.User.username == username_tujuan).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User target tidak ditemukan!")
    if target_user.id == user_sekarang.id:
        raise HTTPException(status_code=400, detail="Kamu tidak bisa mem-follow dirimu sendiri!")
    cek_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == user_sekarang.id,
        models.Follow.following_id == target_user.id
    ).first()
    if cek_follow:
        return {"pesan": f"Kamu sudah mem-follow {username_tujuan} sebelumnya!"}
    follow_baru = models.Follow(follower_id=user_sekarang.id, following_id=target_user.id)
    db.add(follow_baru)
    db.commit()
    return {"pesan": f"Kamu berhasil mem-follow {username_tujuan}!"}


# ─────────────────────────────────────────────
#  FORUM
# ─────────────────────────────────────────────
@app.post("/forum/tulis")
def tulis_forum(
    postingan: schemas.BuatPostingan,
    db: Session = Depends(get_db),
    user_sekarang: models.User = Depends(ambil_user_saat_ini)
):
    post_baru = models.ForumPost(isi_teks=postingan.isi_teks, penulis_id=user_sekarang.id)
    db.add(post_baru)
    db.commit()
    return {"pesan": "Berhasil memposting di forum!"}


@app.get("/forum/baca")
def baca_forum(db: Session = Depends(get_db)):
    semua_post = db.query(models.ForumPost).limit(20).all()
    return {"forum": [{"penulis": p.penulis.username, "isi_teks": p.isi_teks} for p in semua_post]}


# ─────────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────────
@app.post("/report/{username_tujuan}")
def laporkan_user(
    username_tujuan: str,
    laporan: schemas.BuatLaporan,
    db: Session = Depends(get_db),
    user_sekarang: models.User = Depends(ambil_user_saat_ini)
):
    target_user = db.query(models.User).filter(models.User.username == username_tujuan).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User yang mau dilaporkan tidak ditemukan!")
    if target_user.id == user_sekarang.id:
        raise HTTPException(status_code=400, detail="Kamu tidak bisa melaporkan dirimu sendiri!")
    laporan_baru = models.Report(
        pelapor_id=user_sekarang.id,
        dilapor_id=target_user.id,
        alasan=laporan.alasan
    )
    db.add(laporan_baru)
    db.commit()
    return {"pesan": f"Laporan terhadap akun {username_tujuan} berhasil dikirim ke Admin."}


# ─────────────────────────────────────────────
#  KARTU PROFIL
# ─────────────────────────────────────────────
@app.get("/api/kartu-profil/{username_tujuan}")
def data_kartu(username_tujuan: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username_tujuan,
        models.User.is_public == True
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profil Private atau Tidak Ditemukan!")
    return {
        "username": user.username,
        "total_saldo": sum(a.saldo for a in user.akun_trading),
        "jumlah_akun": len(user.akun_trading),
        "status": "Verified Trader"
    }