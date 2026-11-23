#!/bin/bash

echo "Content-type: text/html; charset=utf-8"
echo ""

echo "<html>"
echo "<head>"
echo "    <meta charset='utf-8'>"
echo "    <title>WAN</title>"

cat ../utils/styles.css

echo "</head>"
echo "<body>"

# Torna el valor d'un parametre GET (ex: get_param mode)
get_param() {
    echo "$QUERY_STRING" | tr '&' '\n' | sed -n "s/^$1=//p" | head -n1
}

# Converteix una mascara (24 o 255.255.255.0) a prefix CIDR. Error si no es valida.
masc_a_prefix() {
    local m="$1"
    if [[ "$m" =~ ^[0-9]{1,2}$ ]] && [ "$m" -le 32 ]; then
        echo "$m"; return 0
    fi
    if [[ "$m" =~ ^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$ ]]; then
        local bits=0 oct
        for oct in "${BASH_REMATCH[@]:1:4}"; do
            case "$oct" in
                255) bits=$((bits+8));;
                254) bits=$((bits+7));;
                252) bits=$((bits+6));;
                248) bits=$((bits+5));;
                240) bits=$((bits+4));;
                224) bits=$((bits+3));;
                192) bits=$((bits+2));;
                128) bits=$((bits+1));;
                0)   ;;
                *)   return 1;;
            esac
        done
        echo "$bits"; return 0
    fi
    return 1
}

RE_IP='^([0-9]{1,3}\.){3}[0-9]{1,3}$'
RE_INT='^[a-zA-Z0-9_.-]+$'

comand=$(get_param comand)

case "$comand" in
    iniciar|aturar|estat)
        echo "<h2>WAN $comand </h2>"
        echo "<pre>$(echo "wan $comand" | nc 127.0.0.1 1234)</pre>"
        ;;
    configurar)
        opcio=$(get_param opcio)
        case "$opcio" in
            guardar)
                mode=$(get_param mode)
                int=$(get_param int)
                echo "<h2>WAN configurar</h2>"

                if ! [[ "$int" =~ $RE_INT ]]; then
                    echo "<pre>Error: cal triar una interficie valida</pre>"
                elif [[ "$mode" == "dhcp" ]]; then
                    ordre="wan configurar guardar dhcp $int"
                    echo "<pre>$(echo "$ordre" | nc 127.0.0.1 1234)</pre>"
                    echo "<p>Configuracio guardada: <b>dhcp</b> a <b>$int</b></p>"
                elif [[ "$mode" == "manual" ]]; then
                    ip=$(get_param ip)
                    masc=$(get_param masc)
                    pe=$(get_param pe)
                    dns=$(get_param dns)
                    prefix=$(masc_a_prefix "$masc")

                    if ! [[ "$ip" =~ $RE_IP ]] || [ -z "$prefix" ] || ! [[ "$pe" =~ $RE_IP ]] || ! [[ "$dns" =~ $RE_IP ]]; then
                        echo "<pre>Error: ip, mascara, porta d'enllac o dns no valids</pre>"
                    else
                        # El script wan espera: guardar manual <int> <ip/prefix> <pe> <dns>
                        ordre="wan configurar guardar manual $int $ip/$prefix $pe $dns"
                        echo "<pre>$(echo "$ordre" | nc 127.0.0.1 1234)</pre>"
                        echo "<p>Configuracio guardada: <b>manual</b> a <b>$int</b> ($ip/$prefix)</p>"
                    fi
                else
                    echo "<pre>Error: mode desconegut</pre>"
                fi
                ;;
            *)
                echo "<pre>Error: opcio desconeguda</pre>"
                ;;
        esac
        ;;
    *)
        echo "<pre>Error: comand desconegut</pre>"
        ;;
esac

echo "</body>"
echo "</html>"
