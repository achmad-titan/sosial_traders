from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    is_public = Column(Boolean, default=True) 
    
    # Hubungan ke tabel trading (1 User bisa punya banyak akun trading)
    akun_trading = relationship("TradingAccount", back_populates="pemilik")

class TradingAccount(Base):
    __tablename__ = "trading_accounts"

    id = Column(Integer, primary_key=True, index=True)
    nomor_akun = Column(String(50), unique=True, index=True) # Nomor akun MetaTrader
    nama_server = Column(String(100)) # Contoh: Exness-Real, FBS-Real
    saldo = Column(Float, default=0.0) # Balance uang
    profit_persen = Column(Float, default=0.0) # Win rate / Profit
    user_id = Column(Integer, ForeignKey("users.id")) # ID pemilik akun
    
    # Hubungan balik ke tabel user
    pemilik = relationship("User", back_populates="akun_trading")
    
class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id")) 
    following_id = Column(Integer, ForeignKey("users.id"))
        
class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True)
    isi_teks = Column(String(500)) # Isi komentar/postingan
    penulis_id = Column(Integer, ForeignKey("users.id")) # Siapa yang menulis
    
    # Hubungan balik agar kita tahu siapa penulisnya
    penulis = relationship("User")
    
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    # ID orang yang melapor
    pelapor_id = Column(Integer, ForeignKey("users.id"))
    # ID orang yang dilaporkan
    dilapor_id = Column(Integer, ForeignKey("users.id"))
    # Alasan kenapa dilaporkan
    alasan = Column(String(200))