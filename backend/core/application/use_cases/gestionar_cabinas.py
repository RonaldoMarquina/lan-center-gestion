# Caso de Uso: Gestionar Cabinas


class GestionarCabinas:
    """
    Caso de uso para la gestión de cabinas
    """
    
    def __init__(self, cabina_repository):
        """
        Args:
            cabina_repository: Repositorio de cabinas (puerto)
        """
        self.cabina_repository = cabina_repository
    
    def crear_cabina(
        self,
        numero: int,
        tipo: str,
        especificaciones: dict,
        precio_por_hora: float
    ) -> Cabina:
        """
        Crea una nueva cabina
        
        Args:
            numero: Número de identificación de la cabina
            tipo: Tipo de cabina (basica, gamer, vip)
            especificaciones: Diccionario con las especificaciones técnicas
            precio_por_hora: Precio por hora de uso
            
        Returns:
            Cabina creada
            
        Raises:
            ValueError: Si los datos son inválidos o el número ya existe
        """
        # Verificar que no exista una cabina con ese número
        cabina_existente = self.cabina_repository.buscar_por_numero(numero)
        if cabina_existente:
            raise ValueError(f"Ya existe una cabina con el número {numero}")
        
        # Crear entidad de dominio
        tipo_enum = TipoCabina[tipo.upper()]
        cabina = Cabina(
            id=None,
            numero=numero,
            tipo=tipo_enum,
            estado=EstadoCabina.DISPONIBLE,
            especificaciones=especificaciones,
            precio_por_hora=precio_por_hora
        )
        
        # Persistir
        return self.cabina_repository.guardar(cabina)
    
    def obtener_cabina(self, cabina_id: int) -> Optional[Cabina]:
        """Obtiene una cabina por su ID"""
        return self.cabina_repository.obtener_por_id(cabina_id)
    
    def listar_cabinas_disponibles(self) -> List[Cabina]:
        """Lista todas las cabinas disponibles"""
        return self.cabina_repository.buscar_por_estado(EstadoCabina.DISPONIBLE)
    
    def listar_todas_cabinas(self) -> List[Cabina]:
        """Lista todas las cabinas del sistema"""
        return self.cabina_repository.listar_todas()
    
    def ocupar_cabina(self, cabina_id: int) -> Cabina:
        """
        Marca una cabina como ocupada
        
        Args:
            cabina_id: ID de la cabina a ocupar
            
        Returns:
            Cabina actualizada
            
        Raises:
            ValueError: Si la cabina no existe o no está disponible
        """
        cabina = self.cabina_repository.obtener_por_id(cabina_id)
        if not cabina:
            raise ValueError(f"No se encontró la cabina {cabina_id}")
        
        cabina.ocupar()
        return self.cabina_repository.guardar(cabina)
    
    def liberar_cabina(self, cabina_id: int) -> Cabina:
        """
        Marca una cabina como disponible
        
        Args:
            cabina_id: ID de la cabina a liberar
            
        Returns:
            Cabina actualizada
            
        Raises:
            ValueError: Si la cabina no existe o no está ocupada
        """
        cabina = self.cabina_repository.obtener_por_id(cabina_id)
        if not cabina:
            raise ValueError(f"No se encontró la cabina {cabina_id}")
        
        cabina.liberar()
        return self.cabina_repository.guardar(cabina)
    
    def iniciar_mantenimiento(self, cabina_id: int) -> Cabina:
        """Pone una cabina en mantenimiento"""
        cabina = self.cabina_repository.obtener_por_id(cabina_id)
        if not cabina:
            raise ValueError(f"No se encontró la cabina {cabina_id}")
        
        cabina.iniciar_mantenimiento()
        return self.cabina_repository.guardar(cabina)
    
    def finalizar_mantenimiento(self, cabina_id: int) -> Cabina:
        """Finaliza el mantenimiento de una cabina"""
        cabina = self.cabina_repository.obtener_por_id(cabina_id)
        if not cabina:
            raise ValueError(f"No se encontró la cabina {cabina_id}")
        
        cabina.finalizar_mantenimiento()
        return self.cabina_repository.guardar(cabina)
    
    def actualizar_precio(self, cabina_id: int, nuevo_precio: float) -> Cabina:
        """
        Actualiza el precio por hora de una cabina
        
        Args:
            cabina_id: ID de la cabina
            nuevo_precio: Nuevo precio por hora
            
        Returns:
            Cabina actualizada
        """
        if nuevo_precio <= 0:
            raise ValueError("El precio debe ser positivo")
        
        cabina = self.cabina_repository.obtener_por_id(cabina_id)
        if not cabina:
            raise ValueError(f"No se encontró la cabina {cabina_id}")
        
        cabina.precio_por_hora = nuevo_precio
        return self.cabina_repository.guardar(cabina)
