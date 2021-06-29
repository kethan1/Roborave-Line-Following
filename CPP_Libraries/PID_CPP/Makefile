_PID.so: PID_wrap.cxx PID.cpp
	python3 setup.py build_ext --inplace
PID.py PID_wrap.cxx: PID.i PID.hpp
	swig -c++ -python -py3 -keyword PID.i
clean:
	rm -rf __pycache__ build _PID*.so PID.py PID_wrap.cxx
test: _PID.so
	python3 tester.py
