test_name=${0}

fail () {
  echo 1>&2 "${test_name} FAILED: ${@}"
  exit 1
}

rm -f diagnostics.py*
pyxbgen \
   -u trac26.xsd -m trac26 \
|| fail Unable to build bindings
python3 check-binding.py || fail BindingError check failed
python3 check-validation.py || fail BindingError check failed
