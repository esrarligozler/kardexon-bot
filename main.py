import random
import math
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from collections import Counter


# ================== AYARLAR ==================
BOT_TOKEN = "bot tokeni"
OWNER_ID   = admin id   # SENİN KULLANICI ID'N
# ============================================
def format_card_number(number: str) -> str:
    if len(number) == 16:
        return " ".join(number[i:i+4] for i in range(0, 16, 4))
    if len(number) == 15:
        return " ".join([number[:4], number[4:10], number[10:]])
    return number

def mask_card(number: str) -> str:
    return "**** **** **** " + number[-4:]

def entropy(number: str) -> float:
    counts = Counter(number)
    length = len(number)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())
def has_repeated_blocks(number: str) -> bool:
    return any(d * 4 in number for d in "0123456789")

def has_sequence(number: str) -> bool:
    sequences = ["0123", "1234", "2345", "3456", "4567", "5678", "6789"]
    return any(seq in number for seq in sequences)
def quality_score(number: str, luhn_ok: bool, card_type: str) -> int:
    score = 0
    if luhn_ok:
        score += 40
    if card_type != "Unknown":
        score += 25
    if not has_repeated_blocks(number):
        score += 15
    if not has_sequence(number):
        score += 10
    if entropy(number) > 3.5:
        score += 10
    return score
class AdvancedCC:
    def __init__(self):
        self.config = {
            "Visa": {"prefixes": ["4"], "length": 16, "cvv": 3},
            "Mastercard": {"prefixes": ["51","52","53","54","55","2221","2720"], "length": 16, "cvv": 3},
            "American Express": {"prefixes": ["34","37"], "length": 15, "cvv": 4},
            "Discover": {"prefixes": ["6011","65"], "length": 16, "cvv": 3},
            "JCB": {"prefixes": ["35"], "length": 16, "cvv": 3}
        }

    def luhn_check(self, number: str) -> bool:
        digits = [int(d) for d in number]
        checksum = 0
        parity = len(digits) % 2
        for i, d in enumerate(digits):
            if i % 2 == parity:
                d *= 2
                if d > 9:
                    d -= 9
            checksum += d
        return checksum % 10 == 0

    def calculate_check_digit(self, partial: str) -> str:
        for d in range(10):
            if self.luhn_check(partial + str(d)):
                return str(d)
        return "0"

    def identify_card_type(self, number: str) -> str:
        for name, cfg in self.config.items():
            if len(number) == cfg["length"] and any(number.startswith(p) for p in cfg["prefixes"]):
                return name
        return "Unknown"

    def generate_cvv(self, card_type: str) -> str:
        length = self.config.get(card_type, {}).get("cvv", 3)
        return f"{random.randint(0, 10**length - 1):0{length}d}"

    def generate_expiry(self) -> str:
        """Ay/YYYY formatında (4 haneli yıl)"""
        future = datetime.now() + timedelta(days=random.randint(365, 365*5))
        return future.strftime("%m/%Y")

    def generate_luhn_card(self, card_type: str, prefix: str = None) -> str:
        cfg = self.config[card_type]

        if prefix is not None:
            user_prefix = prefix.strip()
            if not user_prefix.isdigit():
                raise ValueError("BIN yalnızca rakamlardan oluşmalıdır.")
            if len(user_prefix) > cfg["length"] - 1:
                raise ValueError(f"BIN uzunluğu {cfg['length']-1}'den fazla olamaz.")
            selected_prefix = user_prefix
        else:
            selected_prefix = random.choice(cfg["prefixes"])

        remaining = cfg["length"] - len(selected_prefix) - 1
        if remaining < 0:
            raise ValueError("BIN çok uzun, kart numarası oluşturulamaz.")
        body = selected_prefix + str(random.randint(0, 10**remaining - 1)).zfill(remaining)
        return body + self.calculate_check_digit(body)

    def generate_cards(self, card_type: str, count: int = 20, top_n: int = 5,
                       include_extra: bool = True, prefix: str = None):
        cards = []
        for _ in range(count):
            number = self.generate_luhn_card(card_type, prefix)
            ctype = self.identify_card_type(number)
            score = quality_score(number, True, ctype)
            card = {
                "card_type": ctype,
                "number_raw": number,
                "number": format_card_number(number),
                "score": score
            }
            if include_extra:
                card["cvv"] = self.generate_cvv(ctype)
                card["expiry"] = self.generate_expiry()
            cards.append(card)

        cards.sort(key=lambda x: x["score"], reverse=True)
        return cards[:top_n]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TYPE_MAP = {
    "visa": "Visa",
    "mc": "Mastercard",
    "mastercard": "Mastercard",
    "amex": "American Express",
    "americanexpress": "American Express",
    "discover": "Discover",
    "jcb": "JCB"
}

def is_owner(ctx):
    return ctx.author.id == OWNER_ID

@bot.event
async def on_ready():
    print(f"✅ {bot.user} başarıyla giriş yaptı!")

@bot.command(name="komutlar")
async def yardim_menusu(ctx):
    embed = discord.Embed(
        title="📋 Komut Menüsü",
        description="Botun tüm komutları ve filtreleme seçenekleri aşağıda listelenmiştir.",
        color=0x3498db
    )

    embed.add_field(
        name="!kart <tip> [adet] [opsiyonlar]",
        value=(
            "**Açıklama:** Belirtilen türde kredi kartı numarası üretir.\n"
            "**Parametreler:**\n"
            "• `<tip>` → Kart markası (zorunlu)\n"
            "• `[adet]` → Kaç adet üretileceği (1-100, varsayılan: 5)\n"
            "• `[--bin BIN]` → Başlangıç BIN numarası\n"
            "• `[--min-score X]` → Yalnızca skoru ≥ X olanları göster (0-100)\n"
            "• `[--no-sequence]` → Ardışık rakam dizisi içerenleri ele\n"
            "• `[--no-repeat]` → Tekrarlayan blokları (0000 gibi) ele\n\n"
            "**Geçerli tipler:** `visa`, `mc` (mastercard), `amex` (americanexpress), `discover`, `jcb`\n\n"
            "**Örnekler:**\n"
            "`!kart visa 10 --min-score 85 --no-sequence`\n"
            "`!kart mc 5 --bin 519200 --no-repeat`\n"
            "`!kart amex 3 --min-score 90 --no-sequence --no-repeat`"
        ),
        inline=False
    )

    embed.add_field(
        name="!komutlar",
        value="Bu yardım menüsünü gösterir.",
        inline=False
    )

    embed.set_footer(text="Bu bot esrarigozler tarafından yapılmıştır. Destek veya sorularınız için discord.gg/keless")
    await ctx.send(embed=embed)
@bot.command(name="kart")
@commands.check(is_owner)
async def kart_uret(ctx, tip: str = None, adet: int = 5, *, flags: str = ""):
    if tip is None:
        await ctx.send("🚫 Lütfen bir kart tipi belirt. Örn: `!kart visa 5`\n"
                       "Geçerli tipler: `visa`, `mc`, `amex`, `discover`, `jcb`")
        return

    card_class = TYPE_MAP.get(tip.lower())
    if not card_class:
        await ctx.send("❌ Geçersiz kart tipi. Kullanabileceklerin: `visa`, `mc`, `amex`, `discover`, `jcb`")
        return

    if adet < 1 or adet > 100:
        await ctx.send("⚠️ Adet 1-100 arasında olmalı.")
        return

    bin_prefix = None
    min_score = None
    no_sequence = False
    no_repeat = False
    if flags:
        parts = flags.split()
        i = 0
        while i < len(parts):
            part = parts[i]
            if part == "--bin" and i+1 < len(parts):
                bin_prefix = parts[i+1]
                i += 2
            elif part == "--min-score" and i+1 < len(parts):
                try:
                    min_score = int(parts[i+1])
                    if min_score < 0 or min_score > 100:
                        await ctx.send("❌ `--min-score` 0 ile 100 arasında olmalı.")
                        return
                except ValueError:
                    await ctx.send("❌ `--min-score` bir sayı olmalı.")
                    return
                i += 2
            elif part == "--no-sequence":
                no_sequence = True
                i += 1
            elif part == "--no-repeat":
                no_repeat = True
                i += 1
            else:
                i += 1  
    generate_count = max(adet * 10, 200)  
    try:
        cc = AdvancedCC()
        all_cards = cc.generate_cards(
            card_type=card_class,
            count=generate_count,
            top_n=generate_count,   # tümünü al
            include_extra=True,
            prefix=bin_prefix
        )
    except ValueError as e:
        await ctx.send(f"❌ Hata: {e}")
        return
    if min_score is not None:
        all_cards = [c for c in all_cards if c["score"] >= min_score]
    if no_sequence:
        all_cards = [c for c in all_cards if not has_sequence(c["number_raw"])]

    if no_repeat:
        all_cards = [c for c in all_cards if not has_repeated_blocks(c["number_raw"])]

    all_cards.sort(key=lambda x: x["score"], reverse=True)
    cards = all_cards[:adet]

    if not cards:
        await ctx.send("⚠️ Filtrelere uygun kart bulunamadı. Daha geniş kriterler deneyin.")
        return

    card_list = []
    for c in cards:
        ay = c["expiry"][:2]
        yil = c["expiry"][3:]
        line = f"{c['number_raw']}|{ay}|{yil}|{c['cvv']}"
        card_list.append(line)

    filter_desc = []
    if bin_prefix:
        filter_desc.append(f"BIN: {bin_prefix}")
    if min_score is not None:
        filter_desc.append(f"Min Skor: {min_score}")
    if no_sequence:
        filter_desc.append("Ardışık sayı yok")
    if no_repeat:
        filter_desc.append("Tekrar blok yok")
    filter_text = ", ".join(filter_desc) if filter_desc else "Yok"

    embed = discord.Embed(
        title="Üretilen Kartlar",
        description=f"**Kart Tipi:** {card_class}\n**Adet:** {len(card_list)}\n**Filtreler:** {filter_text}",
        color=0x00ff00
    )

    chunk_size = 10
    for i in range(0, len(card_list), chunk_size):
        chunk = card_list[i:i+chunk_size]
        field_value = "\n".join(chunk)
        field_name = "Kart Listesi" if i == 0 else "\u200b"
        embed.add_field(name=field_name, value=f"```{field_value}```", inline=False)

    embed.set_footer(text="Bu bot esrarigozler tarafından yapılmıştır. Destek veya sorularınız için discord.gg/keless")
    await ctx.send(embed=embed)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("⛔ Bu komutu kullanma yetkin yok.")
    else:
        await ctx.send(f"⚠️ Hata: {error}")

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
