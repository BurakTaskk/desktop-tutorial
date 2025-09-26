#!/bin/bash
# OVOS CLI - Shell Script Versiyonu
# Kullanım: ./ovos-cli.sh "hava durumu İstanbul"

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Container adı
CONTAINER_NAME="ovos-weather"

# Varsayılan parametreler
LANG="tr-tr"
WAIT_TIME=3

# Yardım fonksiyonu
show_help() {
    echo -e "${BLUE}🎤 OVOS CLI - Shell Script Versiyonu${NC}"
    echo "=================================="
    echo ""
    echo "Kullanım:"
    echo "  $0 \"komut\" [seçenekler]"
    echo ""
    echo "Örnekler:"
    echo "  $0 \"hava durumu İstanbul\""
    echo "  $0 \"saat kaç\""
    echo "  $0 \"what's the weather\" --lang en-us"
    echo "  $0 \"merhaba\" --wait 5"
    echo ""
    echo "Seçenekler:"
    echo "  --lang, -l    Dil kodu (varsayılan: tr-tr)"
    echo "  --wait, -w    Bekleme süresi saniye (varsayılan: 3)"
    echo "  --help, -h    Bu yardım mesajını göster"
    echo ""
}

# Parametreleri işle
UTTERANCE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --lang|-l)
            LANG="$2"
            shift 2
            ;;
        --wait|-w)
            WAIT_TIME="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            if [[ -z "$UTTERANCE" ]]; then
                UTTERANCE="$1"
            else
                echo -e "${RED}❌ Hata: Bilinmeyen parametre: $1${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# Utterance kontrolü
if [[ -z "$UTTERANCE" ]]; then
    echo -e "${RED}❌ Hata: Komut belirtilmedi!${NC}"
    echo "Kullanım: $0 \"komut\""
    echo "Yardım için: $0 --help"
    exit 1
fi

echo -e "${BLUE}🎤 OVOS CLI - Shell Script${NC}"
echo "=============================="
echo ""

# Container'ın çalışıp çalışmadığını kontrol et
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}❌ Hata: '$CONTAINER_NAME' container'ı çalışmıyor!${NC}"
    echo "Container'ı başlatmak için:"
    echo "  docker start $CONTAINER_NAME"
    echo "Veya yeni container oluşturmak için:"
    echo "  docker run -d --name $CONTAINER_NAME your-image-name"
    exit 1
fi

echo -e "${GREEN}✅ Container '$CONTAINER_NAME' çalışıyor${NC}"
echo -e "${YELLOW}📤 Komut gönderiliyor: '$UTTERANCE'${NC}"

# Python script ile MessageBus'a komut gönder (virtual environment kullan)
docker exec -it "$CONTAINER_NAME" /app/ovos-core/.venv/bin/python -c /app/ovos-cli.py "$@" "

# Çıkış kodu kontrolü
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}🎉 İşlem tamamlandı!${NC}"
else
    echo -e "${RED}💥 İşlem başarısız!${NC}"
    exit 1
fi
